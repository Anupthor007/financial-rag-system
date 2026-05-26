const uploadForm = document.getElementById("uploadForm");

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData();

    formData.append(
        "title",
        document.getElementById("title").value
    );

    formData.append(
        "company_name",
        document.getElementById("company_name").value
    );

    formData.append(
        "document_type",
        document.getElementById("document_type").value
    );

    formData.append(
        "uploaded_by",
        document.getElementById("uploaded_by").value
    );

    formData.append(
        "file",
        document.getElementById("file").files[0]
    );

    const response = await fetch(
        "/documents/upload",
        {
            method: "POST",
            body: formData
        }
    );

    const data = await response.json();

    document.getElementById(
        "uploadMessage"
    ).innerText = data.message;
});


async function searchDocuments() {

    const query = document.getElementById(
        "searchQuery"
    ).value;

    const response = await fetch(
        `/rag/search?query=${query}`,
        {
            method: "POST"
        }
    );

    const data = await response.json();

    const resultsDiv = document.getElementById(
        "results"
    );

    resultsDiv.innerHTML = "";

    data.results.forEach((result) => {

        const resultCard = document.createElement(
            "div"
        );

        resultCard.className = "result-card";

        resultCard.innerHTML = `
            <h3>
                Document ID: ${result.document_id}
            </h3>

            <p>
                ${result.content}
            </p>

            <div class="score">
                Similarity Score:
                ${result.similarity_score}
            </div>
        `;

        resultsDiv.appendChild(resultCard);

    });
}