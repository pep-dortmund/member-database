function count(s, item) {
  return s.length - s.replaceAll(item, "").length;
}
function evenDollars(str) {
  return count(str, "$") % 2 == 0;
}


// Only after everything has rendered in
document.addEventListener("DOMContentLoaded", () => {

  // go trough all "render-katex" inputs
  document.querySelectorAll("div.render-katex").forEach(item => {

    let input = item.querySelector("input");
    let output = item.querySelector("span.katex-output");

    function update() {
      output.innerHTML = input.value;

      // check we have a valid math env
      if (!evenDollars(input.value)) {
        // this prevents submitting the form and shows an error to the user
        input.setCustomValidity("Unclosed $");
        return;
      }

      // this removes the error and allows submission
      input.setCustomValidity("");

      // render math, on error, show error in tooltip and prevent submission
      renderMathInElement(
        output,
        {
          delimiters: [{left: '$', right: '$', display: false}],
          errorCallback: (error, stack) => {
            input.setCustomValidity(stack.toString());
          },
        }
      );
    };

    update();
    input.addEventListener("input", update);
  });
});
