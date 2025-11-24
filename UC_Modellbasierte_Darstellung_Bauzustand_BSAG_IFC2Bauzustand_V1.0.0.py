# Import required libraries
from datetime import datetime
import ifcopenshell
import customtkinter as ctk
import darkdetect
from tkinter import filedialog, messagebox
import os
import sys
import uuid
import getpass

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Try to load application icon
try:
    icon_path = resource_path("Winkel.ico")
    if not os.path.exists(icon_path):
        icon_path = None
except:
    icon_path = None

# Application constants
TITLE = "B+S AG - Modellbasierte Darstellung Bauzustand"
APP_SIZE = (1300, 1000)
FONT = "Segoe UI"
TEXT_FONT_SIZE = 16
TITLE_FONT_SIZE = 24

# Styling constants
STYLING = {
    "corner-radius": 0,
    "checkbox-size": 18
}

# Color scheme
COLORS = {
    "B+S": {
        "fg": "#C80032",    
        "hover": "#505050",  
        "text": "white",
        "tr": "transparent"
    }
}

BLACK = "#000000"
WHITE = "#EEEEEE"

class BIMcollabGUI(ctk.CTk):
    """Main GUI class for BIMcollab smartview generation from IFC files"""
    
    def __init__(self, is_dark):
        """Initialize the GUI application"""
        super().__init__()
        ctk.set_appearance_mode(f'{"dark" if is_dark else "light"}')
        self.resizable(True, True)
        self.title(TITLE)
        self.geometry(f'{APP_SIZE[0]}x{APP_SIZE[1]}')

        # Set application icon if available
        if icon_path and os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except:
                pass

        # Initialize instance variables
        self.selected_files = []
        self.output_path = ctk.StringVar()
        self.use_standard_attribution = ctk.BooleanVar(value=False)
        self.pset_properties = {}
        self.pset_vars = {}
        self.bauphase_vars = {}
        self.rueckbauphase_vars = {}
        self.ifc_schemas = {}

        # Build the GUI
        self.setup_gui()

    def setup_gui(self):
        """Setup the main GUI layout"""
        main_font = ctk.CTkFont(family=FONT, size=TEXT_FONT_SIZE)
        title_font = ctk.CTkFont(family=FONT, size=TITLE_FONT_SIZE, weight="bold")

        # Main container frame
        main = ctk.CTkFrame(self, corner_radius=STYLING["corner-radius"])
        main.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Configure column weights
        for i in range(3):
            main.columnconfigure(i, weight=1)

        # Title label
        title_label = ctk.CTkLabel(
            main, 
            text="Modellbasierte Darstellung Bauzustand",
            font=title_font
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=10, sticky="w", padx=10)
        
        # Subtitle with supported IFC versions
        subtitle_label = ctk.CTkLabel(
            main,
            text="Erstellt Smartviewsets für BIMcollab ZOOM aus IFC-Datei(en) (IFC2x3, IFC4, IFC4x3 kompatibel)",
            font=main_font
        )
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky="w", padx=10)

        # File selection section
        file_frame = ctk.CTkFrame(main, fg_color="transparent")
        file_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5, padx=10)
        file_frame.columnconfigure(0, weight=1)
        
        file_label = ctk.CTkLabel(file_frame, text="Modelle", font=main_font)
        file_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # File listbox (read-only textbox)
        self.file_listbox = ctk.CTkTextbox(file_frame, height=100, font=main_font, corner_radius=STYLING["corner-radius"])
        self.file_listbox.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.file_listbox.configure(state="disabled")
        
        # Button container
        btn_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=(5, 10), padx=10)
        
        # Add files button
        add_btn = ctk.CTkButton(
            btn_frame, 
            text="Hinzufügen", 
            command=self.add_files,
            font=main_font,
            corner_radius=STYLING["corner-radius"],
            fg_color=COLORS["B+S"]["fg"],
            hover_color=COLORS["B+S"]["hover"],
            text_color=COLORS["B+S"]["text"]
        )
        add_btn.pack(side="left", padx=2)
        
        # Delete files button
        del_btn = ctk.CTkButton(
            btn_frame, 
            text="Löschen", 
            command=self.clear_files,
            font=main_font,
            corner_radius=STYLING["corner-radius"],
            fg_color=COLORS["B+S"]["fg"],
            hover_color=COLORS["B+S"]["hover"],
            text_color=COLORS["B+S"]["text"]
        )
        del_btn.pack(side="left", padx=2)

        # Standard attribution section
        attr_frame = ctk.CTkFrame(main, fg_color="transparent")
        attr_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5, padx=10)
        
        attr_label = ctk.CTkLabel(attr_frame, text="Standard-Attributierung", font=main_font)
        attr_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Standard property set checkbox
        self.standard_check = ctk.CTkCheckBox(
            attr_frame,
            text="Standard verwenden (CH_Ing_Uebergeordnet)",
            variable=self.use_standard_attribution,
            command=self.toggle_standard,
            font=main_font,
            corner_radius=STYLING["corner-radius"],
            fg_color=COLORS["B+S"]["fg"],
            hover_color=COLORS["B+S"]["hover"],
            checkbox_width=STYLING["checkbox-size"],
            checkbox_height=STYLING["checkbox-size"]
        )
        self.standard_check.grid(row=1, column=0, sticky="w", padx=10, pady=(5, 10))

        # Custom property selection section (3 columns)
        custom_frame = ctk.CTkFrame(main, fg_color="transparent")
        custom_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=5, padx=10)
        
        for i in range(3):
            custom_frame.columnconfigure(i, weight=1)
        custom_frame.rowconfigure(1, weight=1)

        # PropertySets column
        pset_label = ctk.CTkLabel(custom_frame, text="PropertySets", font=main_font)
        pset_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.pset_frame = ctk.CTkScrollableFrame(custom_frame, fg_color=("gray90", "gray13"), corner_radius=STYLING["corner-radius"])
        self.pset_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=5)

        # Construction phase properties column
        bauphase_label = ctk.CTkLabel(custom_frame, text="Bauphase-Properties", font=main_font)
        bauphase_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        self.bauphase_frame = ctk.CTkScrollableFrame(custom_frame, fg_color=("gray90", "gray13"), corner_radius=STYLING["corner-radius"])
        self.bauphase_frame.grid(row=1, column=1, sticky="nsew", padx=2, pady=5)

        # Demolition phase properties column
        rueckbau_label = ctk.CTkLabel(custom_frame, text="Rückbauphase-Properties", font=main_font)
        rueckbau_label.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        self.rueckbauphase_frame = ctk.CTkScrollableFrame(custom_frame, fg_color=("gray90", "gray13"), corner_radius=STYLING["corner-radius"])
        self.rueckbauphase_frame.grid(row=1, column=2, sticky="nsew", padx=2, pady=5)

        # Output path section
        out_frame = ctk.CTkFrame(main, fg_color="transparent")
        out_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=5, padx=10)
        out_frame.columnconfigure(0, weight=1)
        
        out_label = ctk.CTkLabel(out_frame, text="Output", font=main_font)
        out_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
        
        # Output path entry field
        self.output_entry = ctk.CTkEntry(
            out_frame, 
            textvariable=self.output_path,
            font=main_font,
            corner_radius=STYLING["corner-radius"]
        )
        self.output_entry.grid(row=1, column=0, sticky="ew", padx=(10, 5), pady=(5, 10))
        
        # Browse button
        browse_btn = ctk.CTkButton(
            out_frame, 
            text="...", 
            command=self.browse_output,
            width=50,
            font=main_font,
            corner_radius=STYLING["corner-radius"],
            fg_color=COLORS["B+S"]["fg"],
            hover_color=COLORS["B+S"]["hover"],
            text_color=COLORS["B+S"]["text"]
        )
        browse_btn.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=(5, 10))

        # Create smartviews button
        create_btn = ctk.CTkButton(
            main, 
            text="Smartviews erstellen", 
            command=self.process_files,
            font=main_font,
            height=40,
            corner_radius=STYLING["corner-radius"],
            fg_color=COLORS["B+S"]["fg"],
            hover_color=COLORS["B+S"]["hover"],
            text_color=COLORS["B+S"]["text"]
        )
        create_btn.grid(row=6, column=0, columnspan=3, pady=10, padx=10, sticky="ew")

        # Status log section
        status_frame = ctk.CTkFrame(main, fg_color="transparent")
        status_frame.grid(row=7, column=0, columnspan=3, sticky="nsew", pady=5, padx=10)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(1, weight=1)
        
        status_label = ctk.CTkLabel(status_frame, text="Status", font=main_font)
        status_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Status textbox (read-only log)
        self.status_text = ctk.CTkTextbox(status_frame, height=150, font=main_font, corner_radius=STYLING["corner-radius"])
        self.status_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.status_text.configure(state="disabled")

        # Disclaimer text
        disclaimer_font = ctk.CTkFont(family=FONT, size=10)
        disclaimer_text = ("Diese Software wurde eigenstaendig von den Partnern des jeweiligen Anwendungsfalles entwickelt und stellt eine unabhaengige "
                          "Programmierung dar. Sie steht in keinem direkten oder indirekten Zusammenhang mit buildingSMART International oder einem seiner "
                          "Chapters. Die Nutzung, Weitergabe oder Anpassung der Software erfolgt auf eigene Verantwortung. Fuer Fragen, Feedback oder "
                          "Fehlermeldungen steht das GitHub-Repository des Projektes als zentrale Anlaufstelle zur Verfuegung.\n"
                          "Die bereitgestellte Software dient zur Umsetzung des Anwendungsfalles \"Modelbasierte Darstellung Bauzustand\" und erhebt keinen "
                          "Anspruch auf Vollstaendigkeit oder offizielle Validierung durch buildingSMART oder andere Institutionen.")
        
        disclaimer_label = ctk.CTkLabel(main, text=disclaimer_text, font=disclaimer_font, justify="left", wraplength=1260)
        disclaimer_label.grid(row=8, column=0, columnspan=3, sticky="ew", padx=10, pady=(5, 10))

        # Configure row weights for resizing
        main.rowconfigure(4, weight=1)
        main.rowconfigure(7, weight=1)
        
        # Initialize GUI state
        self.toggle_standard()
        self.log("Bereit")

    def toggle_standard(self):
        """Enable/disable custom property selection based on standard checkbox"""
        if self.use_standard_attribution.get():
            state = "disabled"
        else:
            state = "normal"
        
        # Update PropertySet checkboxes
        for widget in self.pset_frame.winfo_children():
            if isinstance(widget, ctk.CTkCheckBox):
                widget.configure(state=state)
        
        # Update construction phase checkboxes
        for widget in self.bauphase_frame.winfo_children():
            if isinstance(widget, ctk.CTkCheckBox):
                widget.configure(state=state)
        
        # Update demolition phase checkboxes
        for widget in self.rueckbauphase_frame.winfo_children():
            if isinstance(widget, ctk.CTkCheckBox):
                widget.configure(state=state)

    def detect_ifc_schema(self, ifc_file):
        """Detect IFC schema version from the file"""
        try:
            schema = ifc_file.schema
            version_info = {
                'schema': schema,
                'is_ifc2x3': schema.startswith('IFC2X3'),
                'is_ifc4': schema.startswith('IFC4') and not any(x in schema for x in ['IFC4X3', 'IFC4x3']),
                'is_ifc4x3': any(x in schema for x in ['IFC4X3', 'IFC4x3'])
            }
            return version_info
        except Exception as e:
            self.log(f"Warnung: Schema-Erkennung fehlgeschlagen: {e}")
            return {
                'schema': 'UNKNOWN',
                'is_ifc2x3': False,
                'is_ifc4': False,
                'is_ifc4x3': False
            }

    def open_ifc_file_safely(self, filepath):
        """Safely open IFC file with fallback for unsupported schemas"""
        try:
            return ifcopenshell.open(filepath)
        except Exception as e:
            error_msg = str(e).lower()

            # Try fallback method for IFC4X3 files
            if 'unsupported schema' in error_msg and 'ifc4x3' in error_msg:
                self.log(
                    f"Warnung: {os.path.basename(filepath)} verwendet unsupported Schema. Versuche alternative Methode...")
                try:
                    import tempfile
                    import shutil

                    # Create temporary file with schema replacement
                    with tempfile.NamedTemporaryFile(mode='w+', suffix='.ifc', delete=False) as temp_file:
                        temp_filepath = temp_file.name

                        with open(filepath, 'r', encoding='utf-8') as original:
                            content = original.read()

                        # Replace IFC4X3 schema references with IFC4
                        if 'IFC4X3_RC4' in content:
                            content = content.replace('IFC4X3_RC4', 'IFC4')
                            self.log(f"Schema-Fallback: IFC4X3_RC4 -> IFC4 für {os.path.basename(filepath)}")
                        elif 'IFC4X3' in content:
                            content = content.replace('IFC4X3', 'IFC4')
                            self.log(f"Schema-Fallback: IFC4X3 -> IFC4 für {os.path.basename(filepath)}")

                        temp_file.write(content)
                        temp_file.flush()

                    try:
                        ifc_file = ifcopenshell.open(temp_filepath)
                        self.log(f"Erfolg: {os.path.basename(filepath)} mit Schema-Fallback geöffnet")
                        return ifc_file
                    finally:
                        # Clean up temporary file
                        try:
                            os.unlink(temp_filepath)
                        except:
                            pass

                except Exception as fallback_error:
                    self.log(f"Fallback-Methode fehlgeschlagen für {os.path.basename(filepath)}: {fallback_error}")
                    raise e
            else:
                raise e

    def get_compatible_entity_types(self, schema_info):
        """Get list of compatible IFC entity types based on schema version"""
        base_types = ["IfcObjectDefinition", "IfcBuildingElement", "IfcElement", "IfcObject", "IfcProduct"]

        # Add IFC4X3 specific types
        if schema_info['is_ifc4x3']:
            additional_types = [
                "IfcBuiltElement", "IfcElementAssembly", "IfcElementComponent",
                "IfcInfrastructureElement", "IfcCivilElement", "IfcFacility"
            ]
            base_types.extend(additional_types)
        # Add IFC4 specific types
        elif schema_info['is_ifc4']:
            additional_types = ["IfcElementAssembly", "IfcElementComponent"]
            base_types.extend(additional_types)

        return base_types

    def add_files(self):
        """Open file dialog and add selected IFC files"""
        files = filedialog.askopenfilenames(
            title="IFC-Dateien auswählen",
            filetypes=[("IFC Files", "*.ifc")]
        )
        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    filename = os.path.basename(file)

                    try:
                        # Open file and detect schema
                        ifc = self.open_ifc_file_safely(file)
                        schema_info = self.detect_ifc_schema(ifc)
                        self.ifc_schemas[file] = schema_info
                        schema_text = f" ({schema_info['schema']})"
                        self.ifc_schemas[file] = self.detect_ifc_schema(ifc)
                        self.log(f"IFC-Datei geladen: {filename} - Schema: {schema_info['schema']}")
                        # Extract properties from the IFC file
                        self.add_properties_from_ifc(ifc, file)
                    except Exception as e:
                        self.log(f"Fehler beim Laden von {filename}: {e}")
                # Update file listbox
                self.file_listbox.configure(state="normal")
                self.file_listbox.delete("1.0", "end")
                self.file_listbox.insert("end", os.path.basename(file) + schema_text)
                self.file_listbox.configure(state="disabled")

    def update_properties(self):
        """Update property checkboxes based on selected PropertySets"""
        main_font = ctk.CTkFont(family=FONT, size=TEXT_FONT_SIZE)
        selected = [p for p, v in self.pset_vars.items() if v.get()]

        # Clear existing property checkboxes
        for widget in self.bauphase_frame.winfo_children():
            widget.destroy()
        for widget in self.rueckbauphase_frame.winfo_children():
            widget.destroy()
        
        self.bauphase_vars = {}
        self.rueckbauphase_vars = {}
        
        if selected:
            # Collect all properties from selected PropertySets
            props = set()
            for pset in selected:
                props.update(self.pset_properties.get(pset, []))
            
            # Create construction phase property checkboxes
            for prop in sorted(props):
                var = ctk.BooleanVar()
                self.bauphase_vars[prop] = var
                cb = ctk.CTkCheckBox(
                    self.bauphase_frame, 
                    text=prop, 
                    variable=var,
                    font=main_font,
                    corner_radius=STYLING["corner-radius"],
                    fg_color=COLORS["B+S"]["fg"],
                    hover_color=COLORS["B+S"]["hover"],
                    checkbox_width=STYLING["checkbox-size"],
                    checkbox_height=STYLING["checkbox-size"]
                )
                cb.pack(anchor="w", pady=2, padx=5)
            
            # Create demolition phase property checkboxes
            for prop in sorted(props):
                var = ctk.BooleanVar()
                self.rueckbauphase_vars[prop] = var
                cb = ctk.CTkCheckBox(
                    self.rueckbauphase_frame, 
                    text=prop, 
                    variable=var,
                    font=main_font,
                    corner_radius=STYLING["corner-radius"],
                    fg_color=COLORS["B+S"]["fg"],
                    hover_color=COLORS["B+S"]["hover"],
                    checkbox_width=STYLING["checkbox-size"],
                    checkbox_height=STYLING["checkbox-size"]
                )
                cb.pack(anchor="w", pady=2, padx=5)
        
        self.toggle_standard()

    def add_properties_from_ifc(self, ifc, file):
            """Extract PropertySets and properties from IFC file"""
            schema_info = self.detect_ifc_schema(ifc)
            compatible_types = self.get_compatible_entity_types(schema_info)
            self.log(f"Lade Metadaten aus {os.path.basename(file)} (Schema: {schema_info['schema']})")

            try:
                def add_pset(pset_obj):
                    """Helper function to add PropertySet and its properties"""
                    if pset_obj and pset_obj.is_a('IfcPropertySet'):
                        pset_name = getattr(pset_obj, 'Name', None)
                        if pset_name:
                            self.pset_properties.setdefault(pset_name, set())
                            for prop in (getattr(pset_obj, "HasProperties", []) or []):
                                if hasattr(prop, "Name") and prop.Name:
                                    self.pset_properties[pset_name].add(prop.Name)
                
                
                
                processed_entities = 0
                # Process all compatible entity types
                for entity_type in compatible_types:
                    try:
                        entities = ifc.by_type(entity_type)
                        for obj in entities:
                            processed_entities += 1
                            # Check entity's property definitions
                            if hasattr(obj, 'IsDefinedBy') and obj.IsDefinedBy:
                                for rel in obj.IsDefinedBy:
                                    if not rel:
                                        continue
                                    # Handle direct property definitions
                                    if rel.is_a('IfcRelDefinesByProperties'):
                                        add_pset(rel.RelatingPropertyDefinition)
                                    # Handle type property definitions
                                    elif rel.is_a('IfcRelDefinesByType'):
                                        rtype = getattr(rel, "RelatingType", None)
                                        if rtype is not None:
                                            for pset in getattr(rtype, "HasPropertySets", []) or []:
                                                add_pset(pset)
                    except Exception as e:
                        self.log(f"Warnung: Konnte {entity_type} nicht verarbeiten: {e}")
                        continue
                
                self.log(f"Verarbeitet: {processed_entities} Entities, gefunden: {len(self.pset_properties)} PropertySets")
                self.update_property_checkboxes()
            except Exception as e:
                self.log(f"Fehler beim Laden der Metadaten aus {os.path.basename(file)}: {e}")

    def update_file_listbox(self):
        """Update the file listbox display"""
        self.file_listbox.configure(state="normal")
        self.file_listbox.delete("1.0", "end")
        for file in self.selected_files:
            ifc = self.open_ifc_file_safely(file)
            schema_info = self.detect_ifc_schema(ifc)
            schema_text = f" ({schema_info['schema']})"
            self.file_listbox.insert("end", os.path.basename(file) + schema_text)
        self.file_listbox.configure(state="disabled")

    def clear_files(self):
        """Clear all selected files and reset GUI"""
        self.selected_files.clear()
        self.ifc_schemas = {}
        self.update_file_listbox()
        # Clear all property checkboxes
        for widget in self.pset_frame.winfo_children():
            widget.destroy()
        for widget in self.bauphase_frame.winfo_children():
            widget.destroy()
        for widget in self.rueckbauphase_frame.winfo_children():
            widget.destroy()
        self.pset_vars.clear()
        self.bauphase_vars.clear()
        self.rueckbauphase_vars.clear()
        self.pset_properties = {}
        self.log("Dateiliste gelöscht")

    def browse_output(self):
        """Open save file dialog for output path"""
        f = filedialog.asksaveasfilename(defaultextension=".bcsv", filetypes=[("BCSV", "*.bcsv")])
        if f:
            self.output_path.set(f)

    def update_property_checkboxes(self):
        """Update all property checkboxes in the GUI"""
        main_font = ctk.CTkFont(family=FONT, size=TEXT_FONT_SIZE)
        
        # Clear existing checkboxes
        for widget in self.pset_frame.winfo_children():
            widget.destroy()
        for widget in self.bauphase_frame.winfo_children():
            widget.destroy()
        for widget in self.rueckbauphase_frame.winfo_children():
            widget.destroy()
        
        self.pset_vars = {}
        self.bauphase_vars = {}
        self.rueckbauphase_vars = {}
        
        # Create PropertySet checkboxes
        for pset in sorted(self.pset_properties.keys()):
            var = ctk.BooleanVar()
            self.pset_vars[pset] = var
            cb = ctk.CTkCheckBox(
                self.pset_frame, 
                text=pset, 
                variable=var, 
                command=self.update_properties,
                font=main_font,
                corner_radius=STYLING["corner-radius"],
                fg_color=COLORS["B+S"]["fg"],
                hover_color=COLORS["B+S"]["hover"],
                checkbox_width=STYLING["checkbox-size"],
                checkbox_height=STYLING["checkbox-size"]
            )
            cb.pack(anchor="w", pady=2, padx=5)
        
        # Log found PropertySets
        if self.pset_properties:
            self.log(f"PropertySets gefunden: {', '.join(sorted(self.pset_properties.keys()))}")
        else:
            self.log("Keine PropertySets gefunden. Überprüfen Sie die IFC-Dateien.")
        
        self.toggle_standard()

    def _iter_property_sets(self, entity):
        """Iterator to get all PropertySets from an entity"""
        if not hasattr(entity, 'IsDefinedBy') or not entity.IsDefinedBy:
            return
        for rel in entity.IsDefinedBy:
            if not rel:
                continue
            # Direct property definitions
            if rel.is_a('IfcRelDefinesByProperties'):
                pset = getattr(rel, "RelatingPropertyDefinition", None)
                if pset and pset.is_a('IfcPropertySet'):
                    yield pset
            # Type property definitions
            elif rel.is_a('IfcRelDefinesByType'):
                rtype = getattr(rel, "RelatingType", None)
                if rtype is not None:
                    for pset in getattr(rtype, "HasPropertySets", []) or []:
                        if pset and pset.is_a('IfcPropertySet'):
                            yield pset

    def get_phases_from_ifc(self, entity, psets, props):
        """Extract phase numbers from IFC entity properties"""
        def to_float_maybe(val):
            """Try to convert property value to float"""
            if val is None:
                return None

            # Try to get wrapped value
            wrapped = val
            if hasattr(val, "wrappedValue"):
                wrapped = val.wrappedValue
            elif hasattr(val, "Value"):
                wrapped = val.Value

            # Convert to float if possible
            if isinstance(wrapped, (int, float)):
                return float(wrapped)
            if isinstance(wrapped, str):
                s = wrapped.strip().replace(",", ".")
                try:
                    return float(s)
                except ValueError:
                    return None
            return None

        phases = []
        # Iterate through entity's PropertySets
        for pset in self._iter_property_sets(entity):
            pset_name = getattr(pset, 'Name', None)
            if psets and pset_name not in psets:
                continue

            # Check each property
            for prop in getattr(pset, "HasProperties", []) or []:
                name = getattr(prop, "Name", None)
                if props and name not in props:
                    continue

                # Handle single value properties
                if prop.is_a("IfcPropertySingleValue"):
                    num = to_float_maybe(getattr(prop, "NominalValue", None))
                    if num is not None:
                        phases.append(num)
                        continue

                # Handle enumerated value properties
                if prop.is_a("IfcPropertyEnumeratedValue"):
                    ev = getattr(prop, "EnumerationValues", []) or []
                    if ev:
                        num = to_float_maybe(ev[0])
                        if num is not None:
                            phases.append(num)
                            continue

                # Handle list value properties
                if prop.is_a("IfcPropertyListValue"):
                    lv = getattr(prop, "ListValues", []) or []
                    for v in lv:
                        num = to_float_maybe(v)
                        if num is not None:
                            phases.append(num)

        return phases

    def process_files(self):
        """Main processing function: extract phases and generate smartview"""
        # Validate inputs
        if not self.selected_files:
            messagebox.showerror("Fehler", "Keine Dateien ausgewählt")
            return
        if not self.output_path.get():
            messagebox.showerror("Fehler", "Kein Output-Pfad")
            return

        # Determine which PropertySets and properties to use
        if self.use_standard_attribution.get():
            # Use standard Swiss engineering PropertySet
            psets = ["CH_Ing_Uebergeordnet"]
            props_bau = ["Bauphase"]
            props_rueck = ["Rueckbauphase"]
        else:
            # Use custom selection
            psets = [p for p, v in self.pset_vars.items() if v.get()]
            props_bau = [p for p, v in self.bauphase_vars.items() if v.get()]
            props_rueck = [p for p, v in self.rueckbauphase_vars.items() if v.get()]
            if not psets or not props_bau or not props_rueck:
                messagebox.showerror("Fehler", "Bitte PropertySets und Properties für Bau- UND Rückbauphase wählen")
                return

        # Extract phases from all files
        phases = []
        for file in self.selected_files:
            if file.endswith(".ifc"):
                try:
                    # Open IFC file
                    ifc = self.open_ifc_file_safely(file)
                    schema_info = self.ifc_schemas.get(file, self.detect_ifc_schema(ifc))
                    compatible_types = self.get_compatible_entity_types(schema_info)

                    self.log(f"Verarbeite {os.path.basename(file)} mit Schema {schema_info['schema']}")

                    # Process all compatible entity types
                    for entity_type in compatible_types:
                        try:
                            entities = ifc.by_type(entity_type)
                            for obj in entities:
                                # Extract phases from entity
                                phases.extend(
                                    self.get_phases_from_ifc(obj, psets, props_bau + props_rueck)
                                )
                        except Exception as e:
                            self.log(
                                f"Warnung: Konnte {entity_type} in {os.path.basename(file)} nicht verarbeiten: {e}")
                            continue

                except Exception as e:
                    self.log(f"Fehler beim Lesen {os.path.basename(file)}: {e}")

        # Check if any phases were found
        if not phases:
            messagebox.showerror("Fehler", "Keine Phasen gefunden")
            return

        # Sort and deduplicate phases
        phases = sorted(set(phases))
        # Add final phase (one more than the last)
        if len(phases) >= 2:
            phases.append(phases[-1] + 1)

        self.log(f"Gefundene Phasen: {phases}")

        # Generate smartview XML file
        self.generate_smartview(
            phases,
            bauphase_props=[(pset, p) for pset in psets for p in props_bau],
            rueckbau_props=[(pset, p) for pset in psets for p in props_rueck]
        )
        self.log(
            f"Fertig! Es wurden folgende Phasen verarbeitet: {', '.join(str(x) for x in phases)}\n\n"
            f"Der Output wurde unter folgendem Pfad gespeichert:\n{self.output_path.get()}"
        )
        messagebox.showinfo("Erfolg", f"Datei gespeichert:\n{self.output_path.get()}")

    def generate_smartview(self, phases, bauphase_props, rueckbau_props):
        """Generate BIMcollab ZOOM smartview XML file"""
        def w(file, text, level=0):
            """Write indented XML line"""
            file.write(("    " * level) + text + "\n")

        # Get current timestamp and username
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        username = getpass.getuser()
        
        # Generate XML file
        with open(self.output_path.get(), 'w', encoding="utf-8") as f:
            # XML header
            w(f, '<?xml version="1.0"?>')
            w(f, '<bimcollabsmartviewfile>')
            w(f, '<version>6</version>', 1)
            w(f, '<applicationversion>Win - Version: 9.2 (build 9.2.12.0)</applicationversion>', 1)
            w(f, '</bimcollabsmartviewfile>')
            w(f, '<SMARTVIEWSETS>')
            w(f, '<SMARTVIEWSET>', 1)
            w(f, '<TITLE>UC_Modellbasierte_Darstellung_Bauzustand</TITLE>', 2)
            w(f, '<DESCRIPTION>UC_Modellbasierte_Darstellung_Bauzustand</DESCRIPTION>', 2)
            w(f, f'<GUID>{uuid.uuid4()}</GUID>', 2)
            w(f, f'<MODIFICATIONDATE>{now}</MODIFICATIONDATE>', 2)
            w(f, '<SMARTVIEWS>', 2)

            # Create smartview for each phase
            for i, phase in enumerate(phases):
                # Determine phase title
                title = "Bestand" if phase == 0 else ("Endzustand" if i == len(phases) - 1 else phase)
                sv_guid = uuid.uuid4()
                
                # Smartview header
                w(f, '<SMARTVIEW>', 3)
                w(f, f'<TITLE>Bauzustand Phase {title}</TITLE>', 4)
                w(f, '<DESCRIPTION></DESCRIPTION>', 4)
                w(f, f'<CREATOR>{username}</CREATOR>', 4)
                w(f, f'<CREATIONDATE>{now}</CREATIONDATE>', 4)
                w(f, f'<MODIFIER>{username}</MODIFIER>', 4)
                w(f, f'<MODIFICATIONDATE>{now}</MODIFICATIONDATE>', 4)
                w(f, f'<GUID>{sv_guid}</GUID>', 4)
                w(f, '<RULES>', 4)

                # Rules for existing condition (Phase 0)
                if title == "Bestand":
                    for pset, prop in bauphase_props:
                        # Show all elements with Bauphase = 0 in light gray
                        self._write_rule_indent(
                            f, prop, pset, "Equals", phase,
                            "AddSetColored", (204, 204, 204, 255), indent_level=5
                        )
                else:
                    # Rules for construction phases
                    
                    # Rule: Show elements that haven't been built or demolished (gray)
                    for b_pset, b_prop in bauphase_props:
                        for r_pset, r_prop in rueckbau_props:
                            # Elements with Bauphase = 0 AND Rueckbauphase = 0
                            self._write_rule_indent(f, b_prop, b_pset, "Equals", "0.00000000000",
                                                    "And...", (204, 204, 204, 255), indent_level=5)
                            self._write_rule_indent(f, r_prop, r_pset, "Equals", "0.00000000000",
                                                    "AddSetColored", (204, 204, 204, 255), indent_level=5)
                            # Elements with Bauphase = 0 AND Rueckbauphase > current phase
                            self._write_rule_indent(f, b_prop, b_pset, "Equals", "0.00000000000",
                                                    "And...", (204, 204, 204, 255), indent_level=5)
                            self._write_rule_indent(f, r_prop, r_pset, "Greater", phase,
                                                    "AddSetColored", (204, 204, 204, 255), indent_level=5)

                    # Rule: Show elements from previous phases (dark gray)
                    for pset, prop in bauphase_props:
                        self._write_rule_indent(f, prop, pset, "Less", phase, "And...", None, indent_level=5)
                        self._write_rule_indent(f, prop, pset, "Greater", "0.00000000000",
                                                "AddSetColored", (85, 85, 85, 255), indent_level=5)
                        # Rule: Show elements being built in current phase (red)
                        self._write_rule_indent(f, prop, pset, "Equals", phase,
                                                "AddSetColored", (255, 0, 0, 255), indent_level=5)

                    # Rule: Show elements being demolished in current phase (yellow, transparent)
                    for pset, prop in rueckbau_props:
                        self._write_rule_indent(f, prop, pset, "Equals", phase,
                                                "AddSetColored", (255, 249, 10, 255), indent_level=5)
                        self._write_rule_indent(f, prop, pset, "Equals", phase,
                                                "SetTransparent", None, indent_level=5)
                        # Rule: Remove elements demolished in previous phases
                        self._write_rule_indent(f, prop, pset, "Less", phase, "And...", None, indent_level=5)
                        self._write_rule_indent(f, prop, pset, "NotEquals", "0.00000000000",
                                                "Remove", None, indent_level=5)

                # Close smartview
                w(f, '</RULES>', 4)
                w(f,
                  '<INFORMATIONTAKEOFF><PROPERTYSETNAME>None</PROPERTYSETNAME><PROPERTYNAME>None</PROPERTYNAME><OPERATION>0</OPERATION></INFORMATIONTAKEOFF>',
                  4)
                w(f, '<EXPLODEMODE>KeepParentsAndChildren</EXPLODEMODE>', 4)
                w(f, '</SMARTVIEW>', 3)

            # Close XML structure
            w(f, '</SMARTVIEWS>', 2)
            w(f, '</SMARTVIEWSET>', 1)
            w(f, '</SMARTVIEWSETS>')

    def _write_rule_indent(self, f, prop_name, pset, condition_type, value, action_type, color=None, indent_level=0):
        """Write a single rule to the XML file"""
        indent = "    " * indent_level
        parts = [
            "<RULE>",
            "<IFCTYPE>Any</IFCTYPE>",
            "<PROPERTY>",
            f"<n>{prop_name}</n>",
            f"<PROPERTYSETNAME>{pset}</PROPERTYSETNAME>",
            "<TYPE>PropertySet</TYPE><VALUETYPE>DoubleValue</VALUETYPE><UNIT>None</UNIT>",
            "</PROPERTY>",
            "<CONDITION>",
            f"<TYPE>{condition_type}</TYPE>",
            f"<VALUE>{value}</VALUE>",
            "</CONDITION>",
            "<ACTION>",
            f"<TYPE>{action_type}</TYPE>",
        ]
        # Add color if provided
        if color:
            r, g, b, a = color
            parts.append(f"<R>{r}</R><G>{g}</G><B>{b}</B><A>{a}</A>")
        parts.extend(["</ACTION>", "</RULE>"])

        line = indent + "".join(parts) + "\n"
        f.write(line)

    def log(self, msg):
        """Add timestamped message to status log"""
        self.status_text.configure(state="normal")
        self.status_text.insert("end", f"[{datetime.now():%H:%M:%S}] {msg}\n")
        self.status_text.see("end")
        self.status_text.configure(state="disabled")


# Application entry point
if __name__ == "__main__":
    app = BIMcollabGUI(darkdetect.isDark())$

    # Close the splash screen
    try:
        import pyi_splash
        pyi_splash.close()
    except:
        pass

    app.mainloop()
