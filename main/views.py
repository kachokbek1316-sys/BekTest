import time

from django.shortcuts import get_object_or_404, redirect, render

from .models import Answer, Question, Test


QUESTION_TIME = 15


def home(request):
    tests = Test.objects.all().order_by("-id")
    return render(request, "home.html", {"tests": tests})


def categories(request):
    tests = Test.objects.all().order_by("-id")
    return render(request, "categories.html", {"tests": tests})


def leaderboard(request):
    return render(request, "leaderboard.html")


def about(request):
    return render(request, "about.html")


def take_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)

    questions = list(
        Question.objects.filter(test=test)
        .prefetch_related("answers")
        .order_by("order", "id")
    )

    if not questions:
        return render(request, "test.html", {
            "test": test,
            "question": None,
            "error": "Bu testda hozircha savollar mavjud emas.",
            "question_time": QUESTION_TIME,
            "remaining": QUESTION_TIME,
        })

    answers_key = f"bektest_answers_{test.id}"
    timer_key = f"bektest_timer_{test.id}"

    if request.GET.get("restart") == "1":
        request.session.pop(answers_key, None)
        request.session.pop(timer_key, None)
        return redirect("take_test", test_id=test.id)

    saved_answers = request.session.get(answers_key, {})
    timer_data = request.session.get(timer_key, {})

    if not isinstance(saved_answers, dict):
        saved_answers = {}

    if not isinstance(timer_data, dict):
        timer_data = {}

    try:
        question_index = int(request.GET.get("q", "0"))
    except (TypeError, ValueError):
        question_index = 0

    question_index = max(0, min(question_index, len(questions) - 1))

    if question_index == 0 and timer_data.get("completed"):
        saved_answers = {}
        timer_data = {}
        request.session.pop(answers_key, None)
        request.session.pop(timer_key, None)

    question = questions[question_index]
    question_id = str(question.id)

    # Har bir savol uchun alohida boshlanish vaqtini saqlaymiz.
    if question_id not in timer_data:
        timer_data[question_id] = time.time()

    started_at = float(timer_data[question_id])

    def get_remaining():
        elapsed = max(0, time.time() - started_at)
        return max(0, QUESTION_TIME - int(elapsed))

    remaining = get_remaining()
    error = None

    if request.method == "POST":
        action = request.POST.get("action", "next")
        selected_id = request.POST.get("answer", "").strip()

        remaining = get_remaining()
        timed_out = remaining <= 0 or action == "timeout"

        if selected_id and not timed_out:
            valid_answer = Answer.objects.filter(
                id=selected_id,
                question=question,
            ).first()

            if valid_answer:
                saved_answers[question_id] = valid_answer.id

        if not timed_out and not selected_id:
            error = "Davom etish uchun bitta javobni tanla."

        if error:
            request.session[answers_key] = saved_answers
            request.session[timer_key] = timer_data

            return render(request, "test.html", {
                "test": test,
                "question": question,
                "question_number": question_index + 1,
                "total": len(questions),
                "progress": int(
                    ((question_index + 1) / len(questions)) * 100
                ),
                "selected_answer": saved_answers.get(question_id, ""),
                "is_last": question_index == len(questions) - 1,
                "question_time": QUESTION_TIME,
                "remaining": remaining,
                "error": error,
            })

        request.session[answers_key] = saved_answers

        is_last = question_index == len(questions) - 1

        if is_last:
            score = 0

            for item in questions:
                selected = saved_answers.get(str(item.id))

                if selected and item.answers.filter(
                    id=selected,
                    is_correct=True,
                ).exists():
                    score += 1

            total = len(questions)
            percentage = round(score * 100 / total) if total else 0

            timer_data["completed"] = True
            request.session[timer_key] = timer_data

            return render(request, "result.html", {
                "test": test,
                "score": score,
                "total": total,
                "wrong_count": total - score,
                "percentage": percentage,
            })

        next_index = question_index + 1
        next_question_id = str(questions[next_index].id)

        # Keyingi savol uchun yangi 15 soniyalik taymer boshlanadi.
        timer_data[next_question_id] = time.time()
        request.session[timer_key] = timer_data

        return redirect(f"/test/{test.id}/?q={next_index}")

    request.session[answers_key] = saved_answers
    request.session[timer_key] = timer_data

    return render(request, "test.html", {
        "test": test,
        "question": question,
        "question_number": question_index + 1,
        "total": len(questions),
        "progress": int(
            ((question_index + 1) / len(questions)) * 100
        ),
        "selected_answer": saved_answers.get(question_id, ""),
        "is_last": question_index == len(questions) - 1,
        "question_time": QUESTION_TIME,
        "remaining": remaining,
        "error": error,
    })
