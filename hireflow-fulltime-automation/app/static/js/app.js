function bindForm(formId, url, messageId) {
  const form = document.getElementById(formId);
  const message = document.getElementById(messageId);
  if (!form) {
    return;
  }
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (message) {
      message.textContent = "Saving...";
    }
    const response = await fetch(url, {
      method: "POST",
      body: new FormData(form),
    });
    const data = await response.json();
    if (message) {
      message.textContent = response.ok ? "Saved." : JSON.stringify(data);
    }
    if (response.ok) {
      window.location.reload();
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  console.log("HireFlow is ready.");
});
