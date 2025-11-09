from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Min, ProtectedError
from django.db.transaction import atomic
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView, ListView, UpdateView

from bank_transaction_bridge.forms import (
    BankAccountForm,
    ImportBankStatementForm,
    ImportMappingForm,
)
from bank_transaction_bridge.templatetags.bank_transaction_tags import (
    update_current_query,
)
from .models import BankAccount, ImportMapping, Transaction

from .convertors.file_to_json_convertor import (
    CSVFielToBridgeJSONConvertor,
)
from .convertors.json_to_transactions_convertor import (
    JSONToTransactionsConvertor,
)


class TitleMixin:
    title = "Title not set in view!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context


class BulkDeleteMixin:
    def get_success_url(self):
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
            return next_url

        if hasattr(super(), "get_success_url"):
            return super().get_success_url()
        if hasattr(self, "success_url") and self.success_url:
            return str(self.success_url)
        raise ImproperlyConfigured(
            f"{self.__class__.__name__} is missing a success_url. "
            "Define success_url or override get_success_url()."
        )

    def post(self, request, *args, **kwargs):
        ids_to_delete = request.POST.getlist("selected_item_ids")
        if ids_to_delete:
            try:
                self.model.objects.filter(id__in=ids_to_delete).delete()
                messages.success(request, "Selected items were deleted successfully.")
            except ProtectedError as e:
                protected_items = e.protected_objects
                messages.error(
                    request,
                    f"Cannot delete some items because they are in use: {', '.join(str(obj) for obj in protected_items)}",
                )
            return redirect(self.get_success_url())
        selected_ids = request.POST.getlist("items")
        if selected_ids:
            ids_param = ",".join(selected_ids)
            redirect_url = update_current_query(
                request,
                confirm_delete_ids=ids_param,
                next=request.POST.get("next"),
            )
            return redirect(redirect_url)

        return redirect(self.get_success_url())

    def get_queryset(self):
        queryset = super().get_queryset()
        confirm_delete_ids = self.request.GET.get("confirm_delete_ids")
        if confirm_delete_ids:
            return queryset.filter(id__in=confirm_delete_ids.split(","))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_to_delete"] = bool(self.request.GET.get("confirm_delete_ids"))
        return context


class BankAccountCreateView(TitleMixin, CreateView):
    title = "Create Bank Account"
    model = BankAccount
    form_class = BankAccountForm
    success_url = reverse_lazy("bank_transaction_bridge:bank_account_list")


class BankAccountUpdateView(TitleMixin, UpdateView):
    title = "Update Bank Account"
    model = BankAccount
    form_class = BankAccountForm
    success_url = reverse_lazy("bank_transaction_bridge:bank_account_list")


class BankAccoutListView(BulkDeleteMixin, TitleMixin, ListView):
    title = "Bank Accounts"
    model = BankAccount
    success_url = reverse_lazy("bank_transaction_bridge:bank_account_list")


class ImportMappingCreateView(TitleMixin, CreateView):
    title = "Create Import Mapping"
    model = ImportMapping
    form_class = ImportMappingForm
    success_url = reverse_lazy("bank_transaction_bridge:import_mapping_list")


class ImportMappingUpdateView(TitleMixin, UpdateView):
    title = "Update Import Mapping"
    model = ImportMapping
    form_class = ImportMappingForm
    success_url = reverse_lazy("bank_transaction_bridge:import_mapping_list")


class ImportMappingListView(BulkDeleteMixin, TitleMixin, ListView):
    title = "Import Mappings"
    model = ImportMapping
    success_url = reverse_lazy("bank_transaction_bridge:import_mapping_list")


class TransactionListView(BulkDeleteMixin, TitleMixin, ListView):
    title = "Transactions"
    model = Transaction
    template_name = "bank_transaction_bridge/transaction_list.html"

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action and action.startswith("create_connected_item"):
            item_id = action.replace("create_connected_item_", "")
            model_path = getattr(settings, "CONNECTED_ITEM_CLASS", None)
            if not model_path:
                messages.error(
                    self.request,
                    "CONNECTED_ITEM_CLASS not defined in settings",
                )
            else:
                app_label, model_name = model_path.split(".")
                try:
                    ConnectedModelClass = apps.get_model(app_label, model_name)
                    transaction_data = Transaction.objects.get(pk=item_id).get_data()
                    transaction_data["transaction_pk"] = item_id
                    ConnectedModelClass.create_object(request, transaction_data)
                    return redirect(f"{self.request.get_full_path()}#item{item_id}")
                except (LookupError, ValueError) as err:
                    messages.error(self.request, str(err))

        if "remove_duplicates" in request.POST:
            self._remove_duplicate_transactions()
            return redirect(request.get_full_path())

        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["connected_item_class"] = getattr(settings, "CONNECTED_ITEM_CLASS", None)
        data["remove_duplicates"] = True
        order_by = self.request.GET.getlist("order_by")
        if order_by:
            default_ordering = self.model._meta.ordering or []
            data["object_list"] = data["object_list"].order_by(
                *order_by, *default_ordering
            )
        return data

    def _remove_duplicate_transactions(self):
        fields = [
            f.name
            for f in Transaction._meta.fields
            if f.name not in ("id", "created_at")
        ]
        earliest_ids = (
            Transaction.objects.values(*fields)
            .annotate(min_id=Min("id"))
            .values_list("min_id", flat=True)
        )
        Transaction.objects.exclude(id__in=earliest_ids).delete()


def _get_file_to_json_convertor_class(file):
    extension = file.name.rsplit(".", 1)[-1].lower()
    return {"csv": CSVFielToBridgeJSONConvertor}.get(extension)


@atomic
def import_bank_statement_view(request, template=None, extra_context=None):
    template = template or "bank_transaction_bridge/import_file.html"
    extra_context = extra_context or {}
    context = {"title": "Import Bank Statement"}
    result = None
    if request.method == "POST":
        form = ImportBankStatementForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            bank_account = form.cleaned_data["bank_account"]
            import_mapping_object = form.cleaned_data["import_mapping"]
            if not (convertor := _get_file_to_json_convertor_class(file)):
                raise NotImplementedError(
                    f"File {file.name} cannot be converted to JSON. No convertor found for type {file.name.split('.')[0]}."
                )
            json_data = convertor(file, import_mapping_object.mapping).get_json_data()
            result = JSONToTransactionsConvertor(bank_account, json_data).get_result()
    else:
        if not ImportMapping.objects.all():
            context.update({"nomapping": True})
            context.update(extra_context)
            return render(request, template, context)
        form = ImportBankStatementForm()
    context.update({"form": form, "result": result})
    context.update(extra_context)
    return render(
        request,
        template,
        context,
    )
