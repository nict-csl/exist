let AppHeaderButton = {
  template: "#app-header-button-template",
  props: {
    labelName: String,
    color: Object,
    edit: {
      type: Boolean,
      default: false
    },
  },
  delimiters: ['[[', ']]'],
  data(){
    return {
      styleColor:{
        color: null,
        background: this.color
      }
    };
  },
  methods: {
    clickedlabel() {
      this.$emit("clicked", {"color":this.color,"labelName":this.labelName});
    },
    removeLabel(){
      this.$emit('removeLabel',this.labelName)
    },
  },
  created() {
    this.styleColor.color = getTextColor(this.color)
  },
};

let AppHeaderEditModal = {
  template: "#app-header-editmodal-template",
  delimiters: ['[[', ']]'],
  components:{
    "app-header-button": AppHeaderButton,
  },
  props:{
    labels: Array
  },
  data() {
    return {
      labelName: "",
      styleColor:{
        "background": null,
        "color": null,
      },
      colors:[
        "#fa6464",
        "#0a96c8",
        "#ffc2c2",
        "#7cfc00",
        "#fd9535",
        "#f2e5ac",
        "#dd9ef7",
        "#98e6eb",
        "#ffff00",
        "#ff00ff",
      ],
    };
  },
  methods:{
    removeLabel(labelName){
      this.$emit('removeLabel',labelName)
      data = {"label": labelName},
      post(data,post_url_label_delete)
    },
    addLabelSave(){
      if(this.labelName !== ""){
        this.$emit("addLabelSave",{"labelName":this.labelName,"color":this.styleColor.background})
        data = {"labelName":this.labelName,"color":this.styleColor.background}
        post(data,post_url_label_add)
        this.labelName = ""
      }
    },
  },
  computed:{
    setNowColor() {
      return function(color){
        this.styleColor.color = getTextColor(color),
        this.styleColor.background = color
      }
    }

  },
  created(){
    this.styleColor.background = this.colors[Math.floor(Math.random() * this.colors.length-1)];
    this.styleColor.color = getTextColor(this.styleColor.background);
  },
};

let AppHeader = {
  template: "#app-header-template",
  props: {
    labels: Array
  },
  delimiters: ['[[', ']]'],
  components: {
    "app-header-button": AppHeaderButton,
    "app-header-editmodal": AppHeaderEditModal
  },
  methods: {
    ann(label) {
        this.$emit("update", label);
    },
    addLabelSave(label){
        this.$emit("labelupdate",label);
    },
    removeLabel(labelName){
        this.$emit('removelabel',labelName);
    },
  }
};

let AppText = {
  template: "#app-text-template",
  props: {
      text: String,
      anns: Array
  },
  delimiters: ['[[', ']]'],
  data() {
      return {
          startOffset: 0,
          endOffset: 0
      };
  },
  methods: {
        resetRange() {
            this.startOffset = 0;
            this.endOffset = 0;
        },
        makeLabel(startOffset, endOffset) {
            const label = {
                start_offset: startOffset,
                end_offset: endOffset,
                color: "#ffffff",
               check: false
            };
            return label;
        },
        addLabel(label) {
            if (this.isOK()) {
                const ann = {
                    start_offset: this.startOffset,
                    end_offset: this.endOffset,
                    color: label.color,
                    labelName: label.labelName,
                    text: this.text.slice(this.startOffset,this.endOffset),
                    check: true
                };
                this.$emit("add-label", ann);
            }
        },
        selected(e) {
            let start;
            let end;
            if (window.getSelection) {
                const range = window.getSelection().getRangeAt(0);
                const preSelectionRange = range.cloneRange();
                preSelectionRange.selectNodeContents(this.$el);
                preSelectionRange.setEnd(range.startContainer, range.startOffset);
                start = preSelectionRange.toString().replace(/×/g,"").length;
                end = start + range.toString().length;
            }
            this.startOffset = start;
            this.endOffset = end;
        },
        isOK() {
              if (this.startOffset === this.endOffset) {
                  return false;
              }
              if (
                  this.startOffset > this.text.length ||
                  this.endOffset > this.text.length
              ) {
                  return false;
              }
              if (this.startOffset < 0 || this.endOffset < 0) {
                  return false;
              }
              for (let i = 0; i < this.anns.length; i++) {
                  const a = this.anns[i];
                  if (a.start_offset <= this.startOffset && this.startOffset < a.end_offset) {
                      return false;
                  }
                  if (a.start_offset < this.endOffset && this.endOffset <= a.end_offset) {
                      return false;
                  }
                  if (this.startOffset < a.start_offset && a.end_offset < this.endOffset) {
                      return false;
                  }
              }
              return true;
        },
        remove(ann) {
            this.$emit("clear-label", ann);
        },
  },
  computed: {
      sortedAnns() {
          this.anns = this.anns.sort((a, b) => a.start_offset - b.start_offset);
          return this.anns;
      },
      slices() {
          const res = [];
          let left = 0;
          for (let i = 0; i < this.sortedAnns.length; i++) {
              const e = this.sortedAnns[i];
              const l = this.makeLabel(left, e.start_offset);
              res.push(l);
              res.push(e);
              left = e.end_offset;
          }
          const l = this.makeLabel(left, this.text.length);
          res.push(l);
          return res;
        },
      styles() {
          return function(color){
              return {
                  'color': getTextColor(color),
                  'background': color,
              }
          }
      }
  }
};

let App={
  template: "#app-template",
  components: {
    "app-header": AppHeader,
    "app-text": AppText
  },
  delimiters: ['[[', ']]'],
  data(){
    return{
      text: "",
      labels: [],
      anns: []
    }
  },
  created(){
    this.text = text
    var post_labels = labels
    var post_annotations = annotation
    for(const elem of post_labels["labels"]){
        this.labels.push({"color":elem["color"],
                          "labelName":elem["label"]});
    }
    for(const elem of post_annotations["annotation"]){
        this.anns.push({ start_offset: elem["start_off"],
						end_offset: elem["end_off"],
						check: true,
						color: post_labels["labels"].find(e => e["id"] == elem["label_name_id"])["color"],
						text: this.text.slice(elem["start"],elem["end"]),
						labelName: post_labels["labels"].find(e => e["id"] == elem["label_name_id"])["label"]});
    }
  },
  methods: {
    annotate(labelId) {
      this.$refs.apptext.addLabel(labelId);
    },
    addLabel(annotation) {
      this.anns.push(annotation);
    },
    clearLabel(ann) {
      this.anns = this.anns.filter(x => x.start_offset !== ann.start_offset);
    },
    labelUpdate(label){
      this.labels.push({"labelName":label.labelName,"color":label.color})
    },
    removeLabel(labelName){
      this.labels = this.labels.filter(x => x.labelName !== labelName);
    },
    save(){
        data = {"anns":this.anns,"tweet_id":twkey,}
        post(data,post_url)
    }
  },
};

new Vue({
  el: "#main",
  components: {
    "app": App
  },
})

function getCookie(name) {

  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
  return cookieValue
};

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};

function post(data,url){
    var csrftoken = getCookie('csrftoken');
    $.ajax({
        type: "POST",
        data: {
        	"data": JSON.stringify(data),
        },
        url: url,
        traditional: true,
        contentType: "application/json",
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function(data) {
            console.log(data)
        },
        error: function(xhr, status, error) {
            console.log(status + "\n" + "Status: " + xhr.status + "\n" + error);
        }
    })
};

function getTextColor(b_color){
    r = parseInt(b_color.slice(1,3), 16);
    g = parseInt(b_color.slice(3,5), 16);
    b = parseInt(b_color.slice(5,7), 16);
    color = '#000000';
    bg = r * 0.299 + g * 0.587 + b * 0.114;
    if (bg < 186){
        color = '#ffffff'
    };
    return color
};