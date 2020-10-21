from django.db import models
from ..twitter.models import tweet as Tw

class Tweet(models.Model):
    """ツイート"""
    tweet = models.OneToOneField(
        Tw,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    annotated = models.BooleanField('アノテーション済み', default=False)
    checked = models.BooleanField('アノテーション対象', default=False)
    
    def __str__(self):
        return str(self.tweet.id)


class Label(models.Model):
    """ラベル"""
    color = models.CharField('color',default="0",max_length=6)
    label = models.CharField('ラベル名', max_length=255)

    def __str__(self):
        return self.label


class Annotation(models.Model):
    """アノテーション"""
    text_key = models.ForeignKey(Tweet, verbose_name='テキストNo', related_name='text_key', on_delete=models.CASCADE)
    label_name = models.ForeignKey(Label, verbose_name='ラベル名', related_name='labels', on_delete=models.CASCADE)
    annotation = models.CharField('アノテーション内容', max_length=255, blank=True)
    start_off = models.IntegerField('スタートオフセット', default=0)
    end_off = models.IntegerField('エンドオフセット', default=0)

    def __str__(self):
        return self.annotation

