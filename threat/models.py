from django.db import models

# Create your models here.

class Org(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    uuid = models.UUIDField()

    def __str__(self):
        return str(self.id)

class Tag(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    colour = models.CharField(max_length=7, default='#ffffff')
    exportable = models.BooleanField(default=True)
    hide_tag = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def get_textcolor(self):
        red = int(self.colour[1:3], 16)
        green = int(self.colour[3:5], 16)
        blue = int(self.colour[5:7], 16)

        color = '#000000'
        bg = red * 0.299 + green * 0.587 + blue * 0.114
        if bg < 186:
            color = '#ffffff'
        return color


class ObjectReference(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    uuid = models.UUIDField()
    timestamp = models.DateTimeField()
    object_id = models.ForeignKey('Object')
    event = models.ForeignKey('Event')
    referenced_id = models.PositiveIntegerField()
    referenced_type = models.PositiveSmallIntegerField(default=0) # referenced_type represents the numeric value describing what the object reference points to, "0" representing an attribute and "1" representing an object
    relationship_type = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    object_uuid = models.UUIDField()
    referenced_uuid = models.UUIDField()

    def __str__(self):
        return str(self.id)

class Object(models.Model):
    DISTRIBUTION = (
        (0, 'Your Organisation Only'),
        (1, 'This Community Only'),
        (2, 'Connected Communities'),
        (3, 'All Communities'),
        (4, 'Sharing Group'),
    )

    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    meta_category = models.CharField(max_length=255)
    description = models.TextField()
    template_uuid = models.UUIDField()
    template_version = models.PositiveSmallIntegerField()
    event = models.ForeignKey('Event')
    uuid = models.UUIDField()
    timestamp = models.DateTimeField()
    distribution = models.PositiveSmallIntegerField(choices=DISTRIBUTION)
    sharing_group_id = models.PositiveSmallIntegerField(default=0)
    comment = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    attributes = models.ManyToManyField('Attribute')
    objectreferences = models.ManyToManyField(ObjectReference)

    def __str__(self):
        return str(self.id)

class Attribute(models.Model):
    DISTRIBUTION = (
        (0, 'Your Organisation Only'),
        (1, 'This Community Only'),
        (2, 'Connected Communities'),
        (3, 'All Communities'),
        (4, 'Sharing Group'),
        (5, 'Inherit Event'),
    )

    id = models.PositiveIntegerField(primary_key=True)
    type = models.CharField(max_length=64)
    category = models.CharField(max_length=32)
    to_ids = models.BooleanField()
    uuid = models.UUIDField()
    event = models.ForeignKey('Event')
    distribution = models.PositiveSmallIntegerField(choices=DISTRIBUTION)
    timestamp = models.DateTimeField()
    comment = models.TextField(blank=True, null=True)
    sharing_group_id = models.PositiveSmallIntegerField(default=0)
    deleted = models.BooleanField(default=False)
    disable_correlation = models.BooleanField(default=False)
    object_id = models.ForeignKey(Object, blank=True, null=True)
    object_relation = models.CharField(max_length=255, blank=True, null=True)
    value = models.TextField()
    tags = models.ManyToManyField(Tag)
    #data
    #ShadowAttribute = models.ForeignKey(Attribute)

    def __str__(self):
        return str(self.id)

class Event(models.Model):
    THREATLEVEL = (
        (1, 'High'),
        (2, 'Medium'),
        (3, 'Low'),
        (4, 'Undefined'),
    )
    ANALYSIS = (
        (0, 'Initial'),
        (1, 'Ongoing'),
        (2, 'Complete'),
    )
    DISTRIBUTION = (
        (0, 'Your Organisation Only'),
        (1, 'This Community Only'),
        (2, 'Connected Communities'),
        (3, 'All Communities'),
    )

    id = models.PositiveIntegerField(primary_key=True)
    org = models.ForeignKey(Org, related_name='org_id')
    orgc = models.ForeignKey(Org, related_name='orgc_id')
    date = models.DateField()
    threat_level_id = models.PositiveSmallIntegerField(choices=THREATLEVEL, default=4)
    info = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=False)
    uuid = models.UUIDField()
    attribute_count = models.PositiveIntegerField()
    analysis =  models.PositiveSmallIntegerField(choices=ANALYSIS)
    timestamp = models.DateTimeField()
    distribution = models.PositiveSmallIntegerField(choices=DISTRIBUTION)
    proposal_email_lock = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    publish_timestamp = models.DateTimeField()
    sharing_group_id = models.PositiveSmallIntegerField(default=0)
    disable_correlation = models.BooleanField(default=False)
    event_creator_email = models.EmailField(blank=True, null=True)
    tags = models.ManyToManyField(Tag)
    relatedevents = models.ManyToManyField("Event")
    #ShadowAttribute = models.ManyToManyField(Attribute)
    #Galaxy

    def __str__(self):
        return str(self.id)

    def getUniqCategory(self):
        categories = Attribute.objects.filter(event=self.id).values_list('category', flat=True).order_by('category').distinct()
        return categories

    def getUniqType(self):
        types = Attribute.objects.filter(event=self.id).values_list('type', flat=True).order_by('type').distinct()
        return types

    def __lt__(self, other):
        return self.id < other.id

