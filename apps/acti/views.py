from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.http import HttpResponse, HttpResponseServerError, JsonResponse, QueryDict
from django.db.models import Q

from ..twitter.models import tweet as tw
from .forms import SearchForm
from .models import Tweet, Label, Annotation
from pure_pagination.mixins import PaginationMixin

import json



###インデックス###
def index(request):
    return redirect('acti:tweet_list', mode='check')


###リスト画面###
class TweetList(PaginationMixin,ListView):
    context_object_name = 'tweet'
    template_name = 'acti/tweet_list.html'
    context_object_name = 'tweets'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = SearchForm(self.request.GET)
        context['search_form'] = search_form
        return context

    def get_queryset(self):
        if self.kwargs['mode'] == 'check':
            query = Tweet.objects.filter(checked=True, annotated=False).order_by('-tweet__datetime')
        elif self.kwargs['mode'] == 'already':
            query = Tweet.objects.filter(annotated=True).order_by('-tweet__datetime')
        elif self.kwargs['mode'] == 'all':
            query = Tweet.objects.all().order_by('-tweet__datetime')
        else:
            return HttpResponseServerError()
        keyword = self.request.GET.get('keyword')
        if keyword is not None:
            query = query.filter(Q(tweet__text__icontains=keyword)).order_by('-tweet__datetime')
        return query


###アノテーション画面###
def tweet_edit(request, tweet_id=None):
    tw1 = get_object_or_404(tw,id=tweet_id)
    tweet = get_object_or_404(Tweet, tweet=tw1)
    annotation = list(tweet.text_key.all().values())
    labels = list(Label.objects.all().values())
    return render(request,
                  'acti/tweet_edit.html',
                  dict(tweet_id=str(tweet_id),
                       text=tweet.tweet.text,
                       labels={"labels":labels},
                       annotation={"annotation":annotation}))


###閲覧画面###
def tweet_view(request,tweet_id=None):
    tw1 = get_object_or_404(tw,id=tweet_id)
    tweet = get_object_or_404(Tweet, tweet=tw1)
    annotation = list(tweet.text_key.all().order_by('id').values())
    labels = list(Label.objects.all().order_by('id').values())
    return render(request,
                  'acti/tweet_view.html',
                  dict(tweet_id=tweet_id,
                       text=tweet.tweet.text,
                       labels={"labels": labels},
                       annotation={"annotation": annotation}))


###アノテーション追加###
def annotation(request):
    if request.method == 'POST' and request.body:
        dic_str = QueryDict(request.body, encoding='utf-8').getlist("data")[0]
        json_dict = json.loads(dic_str)
        tweet_id = int(json_dict["tweet_id"])
        annotations = json_dict["anns"]
        tw1 = tw.objects.get(id=tweet_id)
        tweet = get_object_or_404(Tweet, tweet=tw1)
        annotation = tweet.text_key.all().order_by('tweet_id')
        annotation.delete()
        add_annotation = []
        for ann in annotations:
            label = Label.objects.filter(label=ann["label"]).first()
            ann_tmp = Annotation(text_key=tweet,
                                 label_name=label,
                                 annotation=ann["text"],
                                 start_off=ann["start_offset"],
                                 end_off=ann["end_offset"])
            add_annotation.append(ann_tmp)
        Annotation.objects.bulk_create(add_annotation)
        tweet.annotated = True
        tweet.save()
        return redirect('acti:tweet_list', mode='check')
    else:
        return HttpResponseServerError()


###ラベル追加###
def add_label(request):
    if request.method == 'POST' and request.body:
        dic_str = QueryDict(request.body, encoding='utf-8').getlist("data")[0]
        json_dict = json.loads(dic_str)
        labelName = json_dict["labelName"]
        color = json_dict["color"]
        label = Label(label=labelName, color=color)
        label.save()
        return HttpResponse(200)
    else:
        return HttpResponseServerError()


###ラベル削除###
def delete_label(request):
    if request.method == 'POST' and request.body:
        dic_str = QueryDict(request.body, encoding='utf-8').getlist("data")[0]
        json_dict = json.loads(dic_str)
        label = json_dict["label"]
        cur = Label.objects.filter(label=label)
        cur.delete()
        return HttpResponse(200)
    else:
        return HttpResponseServerError()


###Annotation Target###
def tweet_get(request):
    dic = QueryDict(request.body, encoding='utf-8')
    pks = dic.getlist("pks")
    pks = [int(pk) for pk in pks]
    try:
        inner_qs = tw.objects.filter(id__in=pks)
        tweets = Tweet.objects.filter(tweet__in=inner_qs)
    except Exception as e:
        pass
    ids = []
    checks=[]
    for tweet in tweets:
        ids.append(tweet.tweet.id)
        checks.append(tweet.checked)
    check_list = {"checks": [ids, checks]}
    return JsonResponse(check_list)


###Annotation Target###
def tweet_add(request):
    dic = QueryDict(request.body, encoding='utf-8')
    pk = dic.get('pk')
    if dic.get('checked') == "true":
        checked = True
    else:
        checked = False
    tw1 = tw.objects.get(id=pk)
    try:
        tweet = Tweet.objects.get(tweet=tw1)
        tweet.checked = checked
    except Exception as e:
        tweet = Tweet(tweet=tw1, checked=checked, annotated=False)
    tweet.save()
    return HttpResponse(200)