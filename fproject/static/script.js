 document.addEventListener("DOMContentLoaded", () => {
    const flashcards = []; 
    let currentCard = 0;

    const flashcardElement = document.getElementById("flashcard");
    const questionElement = document.getElementById("question");
    const answerElement = document.getElementById("answer");

    const form = document.getElementById("flashcard-form");
    const userQuestion = document.getElementById("user-question");
    const userAnswer = document.getElementById("user-answer");

    function displayCard() {
        if(flashcards.length === 0) {
            questionElement.textContent = "No flashcards yet!";
            answerElement.textContent = "";
            return;
        }
        questionElement.textContent = flashcards[currentCard].question;
        answerElement.textContent = flashcards[currentCard].answer;
        flashcardElement.classList.remove("is-flipped");
    }

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const q = userQuestion.value.trim();
        const a = userAnswer.value.trim();
        if(q && a) {
            flashcards.push({question: q, answer: a});
            userQuestion.value = "";
            userAnswer.value = "";
            currentCard = flashcards.length - 1; 
            displayCard();
        }
    });

    document.getElementById("flip-card").addEventListener("click", () => {
        flashcardElement.classList.toggle('is-flipped');
    });

    document.getElementById("next-card").addEventListener("click", () => {
        if(flashcards.length === 0) return;
        currentCard = (currentCard + 1) % flashcards.length;
        displayCard();
    });

    displayCard();
});
