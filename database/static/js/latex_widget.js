var seperateTex = function(string){
  var stringArray = [];
  var index = 0;
  while(index > -1){
    index = string.indexOf('$') > -1 ? string.indexOf('$') : string.length;
    string.substring(0, index) ?
      stringArray.push(string.substring(0, index)) : undefined;
    string = string.substring(index + 1, string.length);
    index = string.indexOf('$');
    if(index > -1){
      string.substring(0, index) ?
        stringArray.push('$' + string.substring(0, index)) : undefined;
      string = string.substring(index+1, string.length);
    }
  }
  return stringArray;
}

var toTex = function(str){
  var stringArray = seperateTex(str);
  try {
    var completeString = "";
    for(var i=0; i<stringArray.length; i++){
      var string = stringArray[i];
      if(string.substring(0, 1) == "$"){
        completeString += katex.renderToString(
          string.substring(1, string.length)
        );
      } else {
        completeString += string;
      }
    }
    return completeString;
  }
  catch(err){
    console.log("Error while parsing tex");
  };
}

var vueApps = {};

document.querySelectorAll('[type="latex"]').forEach(function(item){
  vueApps[item.id] = new Vue({
    el: '#input_group_' + item.id,
    data: {
      title: item.value,
    },
    computed: {
      title_html: function(){
        return toTex(this.title);
      }
    }
  })
});
