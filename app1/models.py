from django.db import models
from app2.models import Profile
import uuid

# Create your models here.
class Project(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    featured_image = models.ImageField(null=True, blank=True, default="default.jpg")
    demo_link = models.CharField(max_length=2000, null=True, blank=True)
    source_link = models.CharField(max_length=2000, null=True, blank=True)
    tags = models.ManyToManyField("Tag", blank=True)
    vote_total = models.IntegerField(default=0, null=True, blank=True)
    vote_ratio = models.IntegerField(default=0, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-vote_ratio", "-vote_total"]

    @property
    def imageURL(self):
        try:
            url = self.featured_image.url
        except:
            url = ''
        return url

    @property
    def reviewers(self):
        queryset = self.review_set.all().values_list("owner__id", flat=True)
        return queryset

    @property
    def getVoteCount(self):
        reviews = self.review_set.all()
        likes = reviews.filter(value="Liked").count()
        totalvotes = reviews.count()

        ratio = (likes / totalvotes) * 100
        self.vote_total = totalvotes
        self.vote_ratio = ratio
        self.save()


class Review(models.Model):
    VOTE_TYPE = (
        ("Liked", "Like"),
        ("Disliked", "Dislike"),
    )
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    body = models.TextField(null=True, blank=True)
    value = models.CharField(max_length=10, choices=VOTE_TYPE)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )

    def __str__(self):
        return self.value

    class Meta:
        unique_together = [["owner", "project"]]


class Tag(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )

    def __str__(self):
        return self.name
