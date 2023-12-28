function debounce(func, wait = 20, immediate = true) {
    var timeout;
    return function () {
        var context = this,
            args = arguments;
        var later = function () {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

function checkSlide() {
    var headings = document.querySelectorAll("h1");

    headings.forEach(function (heading) {
        var contentPosition = heading.getBoundingClientRect().top;
        var viewHeight = window.innerHeight;

        if (contentPosition < viewHeight) {
            heading.classList.add("visible");
            heading.classList.remove("hidden");
        } else {
            heading.classList.add("hidden");
            heading.classList.remove("visible");
        }
    });
}

document.addEventListener("scroll", debounce(checkSlide));
