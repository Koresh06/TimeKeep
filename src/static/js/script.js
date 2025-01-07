function showAlert(message, type = "success") {
  console.log("showAlert called", message, type);  // Проверка вызова функции

  const alertBox = document.createElement("div");
  alertBox.classList.add("alert", `alert-${type}`);
  alertBox.innerText = message;

  // Добавляем алерт в body
  document.body.appendChild(alertBox);

  // Показать алерт
  setTimeout(() => {
    alertBox.classList.add("show");
  }, 100);

  // Убираем алерт через несколько секунд
  setTimeout(() => {
    alertBox.classList.remove("show");
    setTimeout(() => {
      alertBox.remove(); // Удаляем элемент после анимации
    }, 500);
  }, 3000);
}
