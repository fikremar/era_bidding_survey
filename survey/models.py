from django.db import models

class Survey(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    text = models.TextField()
    has_text_response = models.BooleanField(default=False)  # Always requires text
    has_bid = models.BooleanField(default=False)
    text_required_if_yes = models.BooleanField(default=False)  # Text required only if Yes

    def __str__(self):
        return self.text

class Response(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    yes_no = models.BooleanField(null=True)
    text = models.TextField(null=True, blank=True)
    bid_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)