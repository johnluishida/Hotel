const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const toggleButton = document.getElementById('toggleSidebar');

let isOpen = true;

toggleButton.addEventListener('click', () => {
  isOpen = !isOpen;

  if (isOpen) {
    sidebar.classList.remove('sidebar-collapsed');
    mainContent.classList.remove('content-shift-collapsed');
    mainContent.classList.add('content-shift');
  } else {
    sidebar.classList.add('sidebar-collapsed');
    mainContent.classList.remove('content-shift');
    mainContent.classList.add('content-shift-collapsed');
  }
});
const modal = document.getElementById("addAmenityModal");
  const btn = document.getElementById("addAmenityBtn");
  const span = document.querySelector(".close");

  // Open the modal when the button is clicked
  btn.onclick = function () {
    modal.style.display = "block";
  };

  // Close the modal when the close button (×) is clicked
  span.onclick = function () {
    modal.style.display = "none";
  };

  // Close the modal if the user clicks outside of it
  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };

  // Edit button functionality
const editButtons = document.querySelectorAll('.editBtn');
const editModal = document.getElementById('editAmenityModal');
const closeButton = editModal.querySelector('.close');
const editForm = document.querySelector("form");

editButtons.forEach(button => {
  button.addEventListener('click', function() {
    // Get data attributes from the button
    const amenityId = button.getAttribute('data-id');
    const amenityName = button.getAttribute('data-amenity');
    const amenityDescription = button.getAttribute('data-description');
    const amenityPrice = button.getAttribute('data-price');

    // Set values in the modal
    document.getElementById('editAmenityId').value = amenityId;
    document.getElementById('editAmenity').value = amenityName;
    document.getElementById('editDescription').value = amenityDescription;
    document.getElementById('editPrice').value = amenityPrice;

    // Show the modal
    editModal.style.display = "block";
  });
});

// Close the modal when clicking the close button (×)
closeButton.addEventListener('click', function() {
  editModal.style.display = "none";
});

// Close the modal if the user clicks outside of it
window.addEventListener('click', function(event) {
  if (event.target === editModal) {
    editModal.style.display = "none";
  }
});
