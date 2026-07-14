const analyzeBtn = document.getElementById("analyzeBtn");
const resumeFile = document.getElementById("resumeFile");
const loading = document.getElementById("loading");
const result = document.getElementById("result");

const summary = document.getElementById("summary");
const skills = document.getElementById("skills");
const strengths = document.getElementById("strengths");
const weaknesses = document.getElementById("weaknesses");
const suggestions = document.getElementById("suggestions");

analyzeBtn.addEventListener("click", async () => {

    // Check if a file is selected
    if (resumeFile.files.length === 0) {
        alert("Please select a PDF file.");
        return;
    }

    const file = resumeFile.files[0];

    // Create FormData
    const formData = new FormData();
    formData.append("resume", file);

    // Show loading
    loading.classList.remove("hidden");
    result.classList.add("hidden");

    try {

        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        loading.classList.add("hidden");

        if (data.error) {
            alert(data.error);
            return;
        }

        // Show result section
        result.classList.remove("hidden");

        // Summary
        summary.innerText = data.summary;

        // Clear old results
        skills.innerHTML = "";
        strengths.innerHTML = "";
        weaknesses.innerHTML = "";
        suggestions.innerHTML = "";

        // Skills
        data.skills.forEach(skill => {
            const li = document.createElement("li");
            li.innerText = skill;
            skills.appendChild(li);
        });

        // Strengths
        data.strengths.forEach(item => {
            const li = document.createElement("li");
            li.innerText = item;
            strengths.appendChild(li);
        });

        // Weaknesses
        data.weaknesses.forEach(item => {
            const li = document.createElement("li");
            li.innerText = item;
            weaknesses.appendChild(li);
        });

        // Suggestions
        data.suggestions.forEach(item => {
            const li = document.createElement("li");
            li.innerText = item;
            suggestions.appendChild(li);
        });

    }
    catch (error) {

        loading.classList.add("hidden");

        alert("Something went wrong!");

        console.log(error);

    }

});