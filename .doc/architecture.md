# Asset Manager Architecture (Phase 2.8)

```plantuml
@startuml
skinparam packageStyle rectangle
skinparam monochrome true

package "UI Layer" {
  class MainWindow {
    + notebook : ttk.Notebook
    + registry_panel : RegistryPanel
    + config_panel : ConfigPanel
    + build_panel : BuildPanel
    + _on_tab_changed()
  }

  class RegistryPanel {
    + tree : ttk.Treeview
    + filter_entry : ttk.Entry
    + show_hidden_var : BooleanVar
    + refresh_list()
    + _toggle_visibility()
    + _sort_column()
  }

  class ConfigPanel {
    + available_list : Listbox
    + selected_list : Listbox
    + list_enabled()
    + refresh()
  }
}

package "Service Layer" {
  class RegistryService {
    + registry : RegistrySchema
    + list_all()
    + list_enabled()
    + set_ingredient_enabled()
    + refresh_registry()
    + _normalize_type()
  }
}

package "Model Layer" {
  class Ingredient {
    + name : str
    + type : str
    + path : Path
    + is_enabled : bool
    + version : str
  }
}

MainWindow *-- RegistryPanel
MainWindow *-- ConfigPanel
RegistryPanel --> RegistryService
ConfigPanel --> RegistryService
RegistryService "1" *-- "*" Ingredient
@enduml
```

![Asset Manager Architecture](http://www.plantuml.com/plantuml/png/TLDDRzim3BtxLmW-RHqoODSTXcB33WNQeLZsSHHecR65q690CSwoelzzSg2uYfUU7BxtcFT4KRTHGNG_K1MtFkn0O30xS5leSAr7GYFe5497M0W63knwuG6DoXwhAdUO-kUTkOSZIcsUAcCSGOpc0NpuxKFBXnDep3iJMB5XtfgFHdNx_bikColO-QXoj3i8I4dpFGEFKvr5ZiF6TxFaowai1StUKplpdwUgf2q7gz1OrqFei7tpDk7FrHpwmdBEhOAOC_yGnD7Z8JCRJufYCQIUhFWw_SvqxFbWUz-s6Em8CWLY9eJm2sG-zKOmzfQIRqgJKoft7Q4TVVID9w_75ogog7LC-o4iqnVJcBF329wW8Jmvf0JtwTFmdtD297IAxNLs0Ys6r9v7LIJEvi_56gnHHk-ms8N5MC-2fyML5vUzTZqEKFe3qUnzDL14jJvqWgt7y6fUcysAKGQM0SZ_HQl77Luvq0EtIFyVvsusUrbj6AOLYIePIFzu2Un0-mGyfaz6V3ndJNZ3J1aVKQBdaBjpfk8vtQnMYxUn8CjNSRdHgzMdvMLKXVeglwXD_Q4-kTGtTJ69wXP3kn_e7m00)
