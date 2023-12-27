
// get the navbar element
const navbar = document.querySelector('nav');

// define the distance to trigger the color change
const scrollDistance = 650;

// add a scroll event listener to the window object
window.addEventListener('scroll', () => {
    // get the current scrollY value
    const currentScrollY = window.scrollY;

    if (currentScrollY > scrollDistance) {
        // the user has scrolled past the distance
        navbar.classList.add('scrolled-down');
    } else {
        // the user has not scrolled past the distance
        navbar.classList.remove('scrolled-down');
    }
});
