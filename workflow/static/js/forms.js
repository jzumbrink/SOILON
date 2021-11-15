const required_attrs = document.getElementById("form").querySelectorAll("[required]");

//Funktion wird deklariert, welche alle Eingabefelder mit dem Attribut required durchgeht und dann
//den Submit Button dementsprechend verändert.
//Falls alle Felder ausgefüllt, wird der Button u. a. aktiviert und erhält einen grünen Hintergrund
//Falls nicht alle Felder ausfefüllt sind, dann wird der Button u. a. deaktiviert und erhält einen grauen Hintergrund
const refreshSubmitButton = function () {
    let is_form_filled = true;
        for (let i = 0; i < required_attrs.length; i++){
            if(required_attrs[i].value == null || required_attrs[i].value == "" || required_attrs[i].value == 0){
                is_form_filled = false
            }
        }
        let submit_button = document.getElementById("form-submit-button")
        if (is_form_filled){
            submit_button.style.backgroundColor = "#7CB16A";
            submit_button.style.color = "#fff";
            submit_button.disabled = false;
            submit_button.value = "Bestätigen";
        } else{
            submit_button.style.backgroundColor = "#afafaf";
            submit_button.style.color = "#252525";
            submit_button.disabled = true;
            submit_button.value = "Eingabe ungültig";
        }
};

refreshSubmitButton();

for (let i = 0; i < required_attrs.length; i++){
    required_attrs[i].addEventListener("input", refreshSubmitButton);

}