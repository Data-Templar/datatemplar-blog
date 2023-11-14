$(document).ready(function() {$(".select-filters").select2({
    dropdownAutoWidth : true,
    });
});
function filtertable() {
    var dic_results = {}; //disctionnaires des filtres du select
    var list_filters = []; // liste des filtres du select
    var number_columns_name = {}; // dictionnaires entre la position de la colonne et son nom
    $.each($("#tablefiltered th"),function(i,v){
        number_columns_name[i] = $(this).text();
    });
    $.each($(".select-filters"),function(i,v) {
        list_filters.push($(this).attr("name"));
        if (dic_results[$(this).attr("name")] == null) {
            dic_results[$(this).attr("name")] = []
        }
        dic_results[$(this).attr("name")].push($(this).val());
    });

    // Prepare the filters.
    var textsearch = $("#searchtable").val().toLowerCase();
    var nb_filters = list_filters.length;
    var nb_filters_enable = 0; // nb de filtres activés
    // This loop is to calculate the number of initialized filters
    $.each(list_filters,function(k,v){
        if(dic_results[v][0]!=null && dic_results[v].length >= 1){
            nb_filters_enable++;
        };
    });
    $.each($("#tablefiltered tr"), function(key,value){
            if(key!=0){ //don't check the table header
                var nb_compliant_filters = 0;
                var search_result_present = false;
                $(this).find("td").each(function(k,v){
                    // Si la colonne est l'un des filtres. On check si la valeur
                    // est égale au filtre sélectionné
                    try {
                        if(list_filters.includes(number_columns_name[k]) && dic_results[number_columns_name[k]][0].includes($(this).text())){
                            nb_compliant_filters++;
                        }else{
                            if ($(this).text().toLowerCase().indexOf(textsearch) > -1) {
                                search_result_present = true;
                            };
                        };
                    } catch (e) {
                        // console.log(e);
                    };

                });

                if ( nb_compliant_filters == nb_filters_enable && search_result_present) {
                    $(this).toggle(true);
                }else {
                    $(this).toggle(false);
                };
            };
    });
}
