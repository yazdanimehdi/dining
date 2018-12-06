var elem = document.querySelectorAll('input[type="range"]');

var rangeValue = function (event){
    let value = document.getElementById(event.target.name) ;
    value.innerHTML = event.target.value ;
};

for (let i = 0; i < elem.length; i++) {
    elem[i].addEventListener("input", rangeValue);
}