from django.db import models

class Question(models.Model):
    text = models.TextField()
    options = models.JSONField()
    correct_answer = models.CharField(max_length=10)

    def __str__(self):
        return self.text[:50]

    @classmethod
    def create_dummy_questions(cls, num_questions):
        for i in range(num_questions):
            cls.objects.create(
                text=f"Dummy question {i+1}",
                options={"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
                correct_answer="A"
            )