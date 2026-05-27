const filterButtons = Array.from(document.querySelectorAll(".filter"));
const venueCards = Array.from(document.querySelectorAll(".venue-card"));

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const filter = button.dataset.filter;

    filterButtons.forEach((item) => item.classList.toggle("is-active", item === button));

    venueCards.forEach((card) => {
      const types = (card.dataset.type || "").split(" ");
      const visible = filter === "all" || types.includes(filter);
      card.classList.toggle("is-hidden", !visible);
    });
  });
});
