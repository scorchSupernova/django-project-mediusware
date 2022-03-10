from django.shortcuts import redirect
from django.views import generic
from django.views.generic import ListView

from product.models import Variant, Product, ProductImage, ProductVariant
import datetime
from django.core.files.storage import FileSystemStorage


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context

    def post(self, request):
        if request.POST:
             print(request.POST)
             title = request.POST['product_name']
             sku = request.POST['product_sku']
             created_at = datetime.datetime.today()
             updated_at = datetime.datetime.today()
             description = request.POST['product_description']
             product_save = Product.objects.create(title=title, sku=sku, created_at=created_at, updated_at=updated_at, description=description)
             color = request.POST['color_select[]']
             size = request.POST['size_select[]']
             for c in color:
                 if c:
                     prod_variant_save = ProductVariant.objects.create(variant_id=int(c), product_id=product_save.id, created_at=product_save.created_at, updated_at=product_save.updated_at)
             for s in size:
                 if s:
                     prod_variant_save = ProductVariant.objects.create(variant_id=int(c), product_id=product_save.id,
                                                                       created_at=product_save.created_at,
                                                                       updated_at=product_save.updated_at)
             if request.FILES['choosen_file']:
                 choosen_file = request.FILES['choosen_file']
                 fs = FileSystemStorage()
                 filename = fs.save(choosen_file.name, choosen_file)
                 uploaded_file_url = fs.url(filename)
                 file_save = ProductImage.objects.create(file_path=uploaded_file_url, created_at=product_save.created_at, updated_at=product_save.updated_at, product_id=product_save.id)

             return redirect('/product/new_list/')


class CreatedProductListView(ListView):
    paginate_by = 2
    model = Product
    template_name = 'products/list.html'

    def get_context_data(self, **kwargs):
        context = super(CreatedProductListView, self).get_context_data(**kwargs)
        context['product'] = True
        context['variants'] = Variant.objects.filter(active=True).all()
        return context

    def get_queryset(self):
        title = self.request.GET.get('title')
        created = self.request.GET.get('date')
        price_from = self.request.GET.get('price_from')
        price_to = self.request.GET.get('price_to')
        variant = self.request.GET.get('variant', '')

        context = super(CreatedProductListView, self).get_queryset()
        if variant:
            var_type, value = variant.split('_')
            if var_type == 'Size':
                context = context.filter(product_variant_prices__product_variant_one__variant_title=value)
            elif var_type == 'Color':
                context = context.filter(product_variant_prices__product_variant_two__variant_title=value)
            elif var_type == 'Style':
                context = context.filter(product_variant_prices__product_variant_three__variant_title=value)
        if title:
            context = context.filter(title__contains=title)
        if created:
            year, month, day = created.split('-')
            context = context.filter(created_at__year=year,
                                     created_at__month=month,
                                     created_at__day=day)
        if price_from and price_to:
            context = context.filter(product_variant_prices__price__gte=price_from, product_variant_prices__price__lte=price_to)
        elif price_from:
            context = context.filter(product_variant_prices__price__gte=price_from)

        elif price_to:
            context = context.filter(product_variant_prices__price__lte=price_to)
        return context

class ProductEditView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(ProductEditView, self).get_context_data(**kwargs)
        product_id = int(self.kwargs['id'])
        product = Product.objects.get(pk=product_id)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        product_variant = ProductVariant.objects.filter(product_id=product_id)
        context['product_name'] = product.title
        context['product_sku'] = product.sku
        context['product_description'] = product.description
        variant_list = []
        for variant in product_variant:
            variant_list.append(variant.variant_id)
        context['product_variant'] = variant_list
        context['variants'] = list(variants.all())
        context['is_update'] = 1
        print(context)
        return context

    def post(self, request, **kwargs):
        id = self.kwargs['id']
        if request.POST:
             title = request.POST['product_name']
             sku = request.POST['product_sku']
             description = request.POST['product_description']
             product_model = Product.objects.get(pk=id)
             product_model.title = title
             product_model.sku = sku
             product_model.updated_at = datetime.datetime.today()
             product_model.description = description
             product_model.save()
             color = request.POST['color_select[]']
             size = request.POST['size_select[]']
             for c in color:
                 if c:
                     ##Need to add one field for variant type otherwise solution will not match always and that time filter will be like ProductVariant.objects.filter(variant_type=(type_value)).filter(product_id=id).
                     product_variant_model = ProductVariant.objects.filter(product_id=id).update(variant_id=c, updated_at=datetime.datetime.today())
             for s in size:
                 if s:
                     product_variant_model = ProductVariant.objects.filter(product_id=id).update(variant_id=s, updated_at=datetime.datetime.today())

             if request.FILES:
                 if 'choosen_file' in request.FILES:
                     choosen_file = request.FILES['choosen_file']
                     fs = FileSystemStorage()
                     filename = fs.save(choosen_file.name, choosen_file)
                     uploaded_file_url = fs.url(filename)
                     file_save = ProductImage(file_path=uploaded_file_url,updated_at=datetime.datetime.today(), product_id=id)
                     file_save.save()

             return redirect('/product/new_list/')
