//einfache Funktion, um das GET-Formular zu submiten
const submit_formular = function (){
    document.getElementById("db-class-form").submit();
}

const update_disable = function(){
    //Falls es das Element gerade noch gar nicht gibt
    if (document.getElementById("page") == null){
        document.getElementById("previous_page").disabled = true;
        document.getElementById("next_page").disabled = true;
        return
    }
    let page = Number(document.getElementById("page").value);
    //previous page
    if (page == 1){
        document.getElementById("previous_page").disabled = true;
    }else{
        document.getElementById("previous_page").disabled = false;
    }
    //next page
    if (page == document.getElementById("page").max){
        document.getElementById("next_page").disabled = true;
    }else{
        document.getElementById("next_page").disabled = false;
    }
}

//Beim Laden des Dokumentes checken, ob ein Button (oder beide) deaktiviert werden müssen
update_disable();

/*Sorgt dafür, die Seite beim Auswählen einer Option automatisch neu geladen wird
Und beim Laden der anderen Tabelle wird die aktuelle Tabelle ausgeblendet und der Schriftzug mit
"Suchergebnisse werden geladen..." erscheint*/
document.querySelector(".select-menu-db").addEventListener("input", function () {
    document.getElementById("data-results").style.display = "none";
    document.getElementById("data-results-info").style.display = "none";
    document.getElementById("schriftzug-warten").style.visibility = "visible";
    submit_formular();
});

//Formular wird abgesendet, wenn das Eingabefeld für die Seitenzahl nicht mehr fokussiert wird
document.getElementById("page").addEventListener("focusout", submit_formular);

//Wenn sich der Wert der Ergebnisse pro Seite (range) ändert, dann wird dieser auch im numerischen Eingabefeld geändert
//und das Formular wird abgeschickt
document.getElementById("results_per_page_range").addEventListener("change", function () {
    document.getElementById("results_per_page_num").value = document.getElementById("results_per_page_range").value
    submit_formular();
})

//Wenn sich der Wert des numerischen Eingabefeldes für die Ergebnisse pro Seite ändert, dann wird der andere Wert
//ebenfalls aktualisiert
document.getElementById("results_per_page_num").addEventListener("change", function () {
    document.getElementById("results_per_page_range").value = document.getElementById("results_per_page_num").value
})

//Wenn das numerische Eingabefeld nicht mehr fokussiert wird, dann wird das Formular abgeschickt
document.getElementById("results_per_page_num").addEventListener("focusout", function () {
    submit_formular();
})

//Dekrementieren der Seitenzahl, wenn der Button gedrückt wird
document.getElementById("previous_page").addEventListener("click", function () {
    let page = Number(document.getElementById("page").value);
    if (page - 1 > 0){
        document.getElementById("page").value = page - 1;
    }
    submit_formular();
})

//Inkrementieren der Seitenzahl, wenn der Button gedrückt wird
document.getElementById("next_page").addEventListener("click", function () {
    let page = Number(document.getElementById("page").value);
    if (page + 1 <= document.getElementById("page").max){
        document.getElementById("page").value = page + 1;
    }
    submit_formular();
})

//Falls sich die Seitenzahl ändert, dann soll geguckt werden, ob die Buttons für "Nächste Seite" und "Vorherige Seite"
//deaktiviert werden sollen#
document.getElementById("page").addEventListener("input", update_disable)