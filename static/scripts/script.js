function displayLoadingSpinner(toDisplay) {
  let loadingSpinner = document.getElementById("loading-spinner")
  if (toDisplay) {
    loadingSpinner.style.display = 'block'
  } else {
    loadingSpinner.style.display = 'none'
  }
}