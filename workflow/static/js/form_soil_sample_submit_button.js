const save_button = document.getElementById("soil-sample-save-button");
const all_relevant_inputs = document.getElementsByClassName("save-button-input");
const alt_address_input = document.getElementById("id_is_billing_address_sampling_point");
const save_button_div = document.getElementById("soil-sample-save-button-div");
const alt_address_fields = document.getElementById("alt-address-fields")


const adjustSaveButtonSize = function () {
    if(alt_address_input.checked){
        save_button_div.style.width = "50%";
        save_button.style.marginLeft = "0px";
        alt_address_fields.style.visibility = "hidden";
    } else {
        alt_address_fields.style.visibility = "visible";

        save_button_div.style.width = "100%";
        save_button.style.marginLeft = "25%";
    }
}

const styleSaveButton = function () {
    save_button.style.backgroundColor = "#7CB16A";
    save_button.style.color = "#fff";
    save_button.disabled = false;
}

for (let i = 0; i < all_relevant_inputs.length; ++i){
    all_relevant_inputs[i].addEventListener("input", styleSaveButton);
}

alt_address_input.addEventListener("input", adjustSaveButtonSize);

adjustSaveButtonSize();