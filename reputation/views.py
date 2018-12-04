from django.views.generic import ListView, DetailView
from pure_pagination.mixins import PaginationMixin
from django.db.models import Q
from .models import blacklist
from .forms import SearchForm, TargetForm
from .tasks import get_thirty_day_labels, get_thirty_day_data
from django_celery_results.models import TaskResult

class IndexView(PaginationMixin, ListView):
    template_name = 'reputation/index.html'
    context_object_name = 'bls'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = SearchForm(self.request.GET)
        context['search_form'] = search_form
        target_form = TargetForm()
        context['target_form'] = target_form
        count = self.object_list.count()
        context['count'] = count
        #context['source_count'] = self.count_source()
        thirty_day_labels_taskid = get_thirty_day_labels.delay()
        thirty_day_data_taskid = get_thirty_day_data.delay()
        thirty_day_labels = TaskResult.objects.filter(task_name='reputation.tasks.get_thirty_day_labels', status='SUCCESS').order_by('-date_done')
        if len(thirty_day_labels) > 0:
            context['30_day_labels'] = thirty_day_labels[0].result
        thirty_day_data = TaskResult.objects.filter(task_name='reputation.tasks.get_thirty_day_data', status='SUCCESS').order_by('-date_done')
        if len(thirty_day_data) > 0:
            context['30_day_data'] = thirty_day_data[0].result
        return context

    def get_queryset(self):
        query = blacklist.objects.order_by('-datetime')
        #twomonthago = datetime.now() - timedelta(days=60)
        #query = blacklist.objects.exclude(datetime__lte=twomonthago).order_by('-datetime')
        keyword = self.request.GET.get('keyword')
        source = self.request.GET.get('source')
        if keyword is not None:
            query = query.filter(Q(ip=keyword)|Q(domain__contains=keyword)|Q(url__contains=keyword))
        if source is not None:
            query = query.filter(source=source)
        return query

    def count_source(self):
        data = {}
        for src in blacklist.SOURCES:
            count = self.object_list.filter(source=src[0]).count()
            data[src[0]] = count
        return data

class DetailView(DetailView):
    model = blacklist
    template_name = 'reputation/detail.html'

