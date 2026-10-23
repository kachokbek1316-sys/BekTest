document.addEventListener("DOMContentLoaded", function () {
    const timer = document.querySelector("[data-timer]");
    const number = document.querySelector("[data-timer-number]");
    const form = document.querySelector("[data-quiz-form]");
    const action = document.querySelector("[data-quiz-action]");
    const button = document.querySelector("[data-submit-button]");
    const timeoutMessage = document.querySelector("[data-timeout-message]");

    if (!timer || !number || !form) {
        return;
    }

    let seconds = Number.parseInt(timer.dataset.seconds, 10);

    if (!Number.isFinite(seconds)) {
        seconds = 15;
    }

    seconds = Math.max(0, seconds);
    number.textContent = seconds;

    let finished = false;

    function submitQuestion() {
        if (finished) return;

        finished = true;

        if (action) {
            action.value = "timeout";
        }

        if (timeoutMessage) {
            timeoutMessage.hidden = false;
        }

        if (button) {
            button.disabled = true;
            button.textContent = "Vaqt tugadi...";
        }

        HTMLFormElement.prototype.submit.call(form);
    }

    if (seconds <= 0) {
        submitQuestion();
        return;
    }

    const countdown = setInterval(function () {
        if (finished) {
            clearInterval(countdown);
            return;
        }

        seconds = Math.max(0, seconds - 1);
        number.textContent = seconds;

        if (seconds <= 5) {
            timer.classList.add("timer-warning");
        }

        if (seconds === 0) {
            clearInterval(countdown);
            submitQuestion();
        }
    }, 1000);

    form.addEventListener("submit", function () {
        finished = true;
        clearInterval(countdown);
    });
});