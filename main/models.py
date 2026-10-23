
from django.db import models


class Test(models.Model):
    title = models.CharField(max_length=200, verbose_name="Test nomi")
    description = models.TextField(
        blank=True,
        verbose_name="Test haqida"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan vaqt"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Test"
        verbose_name_plural = "Testlar"

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Test"
    )
    text = models.TextField(verbose_name="Savol")
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="Tartib raqami"
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"

    def __str__(self):
        return self.text[:100]


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Savol"
    )
    text = models.CharField(max_length=500, verbose_name="Javob")
    is_correct = models.BooleanField(
        default=False,
        verbose_name="To‘g‘ri javobmi?"
    )

    class Meta:
        verbose_name = "Javob"
        verbose_name_plural = "Javoblar"

    def __str__(self):
        return self.text
