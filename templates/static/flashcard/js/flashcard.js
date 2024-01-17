function flip_card(id){
    let card = document.getElementById(id);

    if(card.style.display == 'none' || card.style.display == ''){
        card.style.display = 'block';
    }else{
        card.style.display = 'none';
    }
}