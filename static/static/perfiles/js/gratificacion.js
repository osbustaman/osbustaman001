function reverseNumber(input) {
  return [].map.call(input, function(x) {
    return x;
  }).reverse().join(''); 
}
      
function plainNumber(number) {
  return number.split('.').join('');
}
      
function splitInDots(input) {
  var value = input.value,
  plain = plainNumber(value),
  reversed = reverseNumber(plain),
  reversedWithDots = reversed.match(/.{1,3}/g).join('.'),
  normal = reverseNumber(reversedWithDots);
  //console.log(plain,reversed, reversedWithDots, normal);
  input.value = normal;
}
      
function isNumberKey(evt){
    var charCode = (evt.which) ? evt.which : event.keyCode
    if (charCode > 31 && (charCode < 48 || charCode > 57))
        return false;
    return true;
}
      
function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

function impuestoX(baseTributableX, tipo){
  var impuesto = 0;
  var i = 0;

  switch(tipo){
    case undefined:
    case "":
    case null: 
    case 1: divisor=1; break; //mensual
    case 2: divisor=2; break; //quincenal
    case 3: divisor=(30/7); break; //semanal
    case 4: divisor=30; break; //diario
  }

  // baseTributable * factor - rebaja*utm
  //impuestoUTMdata["0.0"].desde;
  for (i in impuestoUTMdata) {
    if(baseTributableX > (utm*parseFloat(impuestoUTMdata[i].desde))/divisor && baseTributableX <= (utm*parseFloat(impuestoUTMdata[i].hasta))/divisor){
      impuesto = baseTributableX*impuestoUTMdata[i].factor-utm*(impuestoUTMdata[i].rebaja)/divisor ;    
    }
  }
return impuesto;
}

function valorHoraExtraX(sueldoX, tipoContrato, horasTrabajadasSemana, horasTrabajadasDiario){
  // ex. usage: valorHoraExtraX(100000, "Mensual", 45, 0)
  // ex. usage: valorHoraExtraX(100000, "Mensual", 40, 0)
  // ex. usage: valorHoraExtraX(30000, "Diario", 0, 5)
  switch(tipoContrato){
    case undefined:
    case "":
    case null: 
    case "Mensual": horaOrdinaria = sueldoX*(28/(30*horasTrabajadasSemana*4)); break; //mensual
    case "Quincenal": horaOrdinaria = sueldoX/(horasTrabajadasSemana*2); break; //quincenal
    case "Semanal": horaOrdinaria = sueldoX/horasTrabajadasSemana; break; //semanal
    case "Diario": horaOrdinaria = sueldoX/horasTrabajadasDiario; break; //diario
    case "Variable": break; // IMM/horasTrabajadasSemenal * cantidad horas extras
  }

  valorHoraExtra = horaOrdinaria*1.5;

return valorHoraExtra;
}

/*function editUTM(){
  if(utmcheck.checked){
    utminput.removeAttribute("readonly");

  }
  else{
    utminput.setAttribute("readonly","readonly");
  }
}*/

function startCalc(){
  interval = setInterval("calc()",1);
}

function calc(){

  if(document.formulario.sueldoBase.value == '' || document.formulario.sueldoBase.value == null){
    sueldoBase = 0;
  }
  else{
    sueldoBase = parseInt((document.formulario.sueldoBase.value).split('.').join("")); // .split('.').join("") quita los puntos
  }
  
  /******************+**********/
  /**** OBTENCION DE DATOS ****/
  /***************************/
  // gratificación: grat o 25% de base, el q sea menor.
  //if(document.formulario.gratificacionCheck.checked){
    if(grat>(sueldoBase+horasExtra+bono+comisiones)*0.25){ 
      gratificacion = Math.round((sueldoBase+horasExtra+bono+comisiones)*0.25);
      document.formulario.gratificacion.value = numberWithCommas(Math.round(gratificacion));
    }
    else{
      gratificacion = Math.round(grat);
      document.formulario.gratificacion.value = numberWithCommas(Math.round(gratificacion));
    }
  //}
  //else{
    //gratificacion = 0;
    //document.formulario.gratificacion.value = numberWithCommas(Math.round(gratificacion));
  //}

  // leer los demas campos antes de total haberes
  if(document.formulario.comisiones.value == '' || document.formulario.comisiones.value == null){comisiones = 0;}else{
    comisiones = parseInt((document.formulario.comisiones.value).split('.').join(""));
  }
  if(document.formulario.bono.value == '' || document.formulario.bono.value == null){bono = 0;}else{
    bono = parseInt((document.formulario.bono.value).split('.').join(""));
  }
  if(document.formulario.horasExtra.value == '' || document.formulario.horasExtra.value == null){horasExtra = 0;}else{
    horasExtra = parseInt((document.formulario.horasExtra.value).split('.').join(""));
  }

  /********************+**********/
  /**** SECCION HORAS EXTRAS ****/
  /*****************************/
  horasExtra = Math.round(horasExtra*valorHoraExtraX((sueldoBase), "Mensual", 45, 0));
  //horasExtra = Math.round(horasExtra*(((sueldoBase/30)*28)/180)*1.5);

}

function stopCalc(){
  clearInterval(interval);
}

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip(); 
   
    $('#utm').attr('placeholder', '$'+numberWithCommas(utm.toString().replace(".",",")) ); 
    $('#uf').attr('placeholder', '$'+numberWithCommas(uf.toString().replace(".",",")) );
    $('#imm').attr('placeholder', '$'+numberWithCommas(imm.toString().replace(".",",")) );  
});

$('a.tooltipx').webuiPopover({width:300, animation:'pop'});