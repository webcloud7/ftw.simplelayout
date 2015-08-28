suite("Toolbox", function() {
  "use strict";

  var Toolbox;

  setup(function(done) {
    require(["app/toolbox/Toolbox"], function(_Toolbox) {
      Toolbox = _Toolbox;
      done();
    });
  });

  test("is a constructor function", function() {
    assert.throw(Toolbox, TypeError, "Toolbox constructor cannot be called as a function.");
  });

  test("attaches to target container", function() {
    var toolbox = new Toolbox({layouts: [0]});
    var target = $("<div></div>");

    toolbox.attachTo(target);

    var addedNodes = $.map(target.children(), function(e) {
      return [{tag: e.tagName, id: e.id, classes: e.className}];
    });
    assert.deepEqual(addedNodes, [{tag: "DIV", id: "sl-toolbox", classes: "sl-toolbox"}]);
  });

  test("disables components", function() {
    var toolbox = new Toolbox({layouts: [0]});
    var target = $("<div></div>");

    toolbox.attachTo(target);

    toolbox.disableComponents();

    assert.equal("sl-toolbox-components disabled", toolbox.element.find(".sl-toolbox-components")[0].className);
  });

  suite("components", function() {
    test("can set components", function() {
      var toolbox = new Toolbox({
        layouts: [0],
        components: {

          addableBlocks: {
            listingblock: {
              title: "Listingblock",
              description: "can list things",
              contentType: "listingblock",
              formUrl: "http://www.google.com",
              actions: {
                edit: {
                  name: "edit",
                  description: "Edit this block"
                }
              }
            },
            textblock: {
              title: "Textblock",
              description: "can show text",
              contentType: "textblock",
              formUrl: "http://www.bing.com",
              actions: {
                edit: {
                  name: "edit",
                  description: "Edit this block"
                }
              }
            }
          },
          layoutActions: {
            actions: {
              move: {
                class: "iconmove move",
                title: "Move this layout arround."
              },
              delete: {
                class: "icondelete delete",
                title: "Delete this layout."
              }
            }
          }
        }
      });

      var target = $("<div></div>");
      toolbox.attachTo(target);

      var addedNodes = $.map(target.find(".sl-toolbox-component"), function(e) {
        return {title: $(e).text().trim(), description: $(e).attr("title"), iconClass: $("i", e).attr("class"), formUrl: $(e).data("form_url")};
      });

      assert.deepEqual(addedNodes, [{title: "Listingblock", description: "can list things", iconClass: "icon-listingblock", formUrl: "http://www.google.com"}, {title: "Textblock", description: "can show text", iconClass: "icon-textblock", formUrl: "http://www.bing.com"}]);
    });

    test("raises exception when no layout is defined", function() {
      assert.throws(function(){
        var toolbox = new Toolbox();
        toolbox();
      }, Error, "No layouts defined.");
    });

    test("can allow layouts by column count", function() {
      var toolbox = new Toolbox({
        layouts: [1, 2, 4]
      });
      var target = $("<div></div>");

      toolbox.attachTo(target);

      var addedNodes = $.map(target.find(".sl-toolbox-layout"), function(e) {
        return $(e).data("columns");
      });
      assert.deepEqual(addedNodes, [1, 2, 4]);
    });

    test("toolbox components are sorted asc", function() {
      /*
      PhantomJS ignores the caseFirst option for localeComparison
      So skip the test if running in phantonJS environment.
       */
      if(!window.mochaPhantomJS) {
        var toolbox = new Toolbox({
          layouts: [0],
          components: {
            addableBlocks: {
              cue: {title: "Ü"},
              r: {title: "r"},
              ue: {title: "ü"},
              d: {title: "d"},
              coe: {title: "Ö"},
              o: {title: "o"},
              oe: {title: "ö"},
              u: {title: "u"},
              cae: {title: "Ä"},
              a: {title: "a"}
            }
          }
        });
        var target = $("<div></div>");
        toolbox.attachTo(target);
        var components = $.map(target.find(".sl-toolbox-components a"), function(e) {
          return e.text.trim();
        });
        assert.deepEqual(components, ["a", "Ä", "d", "o", "ö", "Ö", "r", "u", "ü", "Ü"]);
      }
    });

  });

});
