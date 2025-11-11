#!/usr/bin/env python3
import os
import sys
import json
import argparse
import xml.etree.ElementTree as ET

try:
    import pyfiglet
    from termcolor import colored
except ImportError:
    print("Please install required packages: pip install pyfiglet termcolor")
    sys.exit(1)

# -------------------- CONSTANTS / CONFIG --------------------
BASE_SRC = "src/main/java"
CONFIG_DIR = os.path.expanduser("~/.springgen")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "base_package": "com.example.demo",
    "persistence_package": "auto",
    "folders": {
        "entity": "model",
        "repository": "repository",
        "service": "service",
        "controller": "controller"
    }
}

MAVEN_NS = {'m': 'http://maven.apache.org/POM/4.0.0'}

# -------------------- CONFIG HELPERS --------------------
def ensure_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        print(colored("⚙️  Default config created at ~/.springgen/config.json", "yellow"))

def load_config():
    ensure_config()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(data):
    ensure_config()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# -------------------- UX HELPERS --------------------
def print_banner():
    text = pyfiglet.figlet_format("SpringGen", font="slant")
    print(colored(text, "cyan"))
    print(colored("💡 Spring Boot CRUD Generator CLI\n", "yellow"))

def ask_yes_no(question, default="y"):
    ans = input(f"{question} [y/n] (default {default}): ").strip().lower()
    if not ans:
        ans = default
    return ans.startswith("y")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def write_file(path, content):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Created {path}")

# -------------------- (Optional) Detect persistence package --------------------
def _parse_semver(v: str):
    if not v:
        return (0, 0, 0)
    parts = v.split(".")
    nums = []
    for p in parts[:3]:
        num = ""
        for ch in p:
            if ch.isdigit():
                num += ch
            else:
                break
        nums.append(int(num) if num else 0)
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)

def _get_text(el):
    return el.text.strip() if el is not None and el.text else None

def _resolve_property(val, props):
    if not val:
        return val
    if val.startswith("${") and val.endswith("}"):
        key = val[2:-1]
        return props.get(key, val)
    return val

def _collect_properties(root):
    props = {}
    props_el = root.find("m:properties", MAVEN_NS)
    if props_el is not None:
        for child in list(props_el):
            tag = child.tag.split("}")[-1]
            props[tag] = _get_text(child)
    return props

def _detect_spring_boot_version_from_parent(root, props):
    parent = root.find("m:parent", MAVEN_NS)
    if parent is None:
        return None
    g = _get_text(parent.find("m:groupId", MAVEN_NS))
    a = _get_text(parent.find("m:artifactId", MAVEN_NS))
    v = _resolve_property(_get_text(parent.find("m:version", MAVEN_NS)), props)
    if g == "org.springframework.boot" and a == "spring-boot-starter-parent":
        return v
    return None

def _detect_spring_boot_version_from_props(props):
    for key in ("spring-boot.version", "springboot.version", "spring_boot_version"):
        if key in props and props[key]:
            return props[key]
    return None

def detect_persistence_package_from_pom():
    """Return 'jakarta.persistence' for Boot >=3, else 'javax.persistence' (best effort)."""
    pom_file = "pom.xml"
    try:
        if os.path.exists(pom_file):
            tree = ET.parse(pom_file)
            root = tree.getroot()
            props = _collect_properties(root)
            ver = _detect_spring_boot_version_from_parent(root, props) or _detect_spring_boot_version_from_props(props)
            if ver:
                major, minor, patch = _parse_semver(_resolve_property(ver, props))
                return "jakarta.persistence" if (major, minor, patch) >= (3, 0, 0) else "javax.persistence"
    except Exception as e:
        print(colored(f"⚠️  Could not detect Spring Boot version automatically ({e}). Defaulting to javax.persistence.", "yellow"))
    return "javax.persistence"

_PERSISTENCE_PKG = None
def get_persistence_pkg(config):
    global _PERSISTENCE_PKG
    if _PERSISTENCE_PKG is None:
        forced = config.get("persistence_package", "auto")
        if forced == "auto":
            _PERSISTENCE_PKG = detect_persistence_package_from_pom()
        elif forced in ("jakarta.persistence", "javax.persistence"):
            _PERSISTENCE_PKG = forced
        else:
            print(colored(f"⚠️  Unknown persistence_package '{forced}', defaulting to javax.persistence", "yellow"))
            _PERSISTENCE_PKG = "javax.persistence"
        print(colored(f"📦 Using JPA imports from: `{_PERSISTENCE_PKG}`", "green"))
    return _PERSISTENCE_PKG

# -------------------- IMPORTS (Context-aware) --------------------
def _add_if_external(imports: list, target_pkg: str, current_pkg: str, type_name: str):
    """Add an import only if target_pkg != current_pkg."""
    if target_pkg and target_pkg != current_pkg:
        imports.append(f"import {target_pkg}.{type_name};")

def gen_imports(base_pkg: str, entity: str, layer: str, layer_pkgs: dict, config: dict) -> str:
    """Generate minimal, context-aware imports per layer."""
    persistence_pkg = get_persistence_pkg(config)
    lines = [f"package {base_pkg};", ""]

    def add_if_external(target_pkg: str, type_name: str):
        if target_pkg and target_pkg != base_pkg:
            lines.append(f"import {target_pkg}.{type_name};")

    if layer == "entity":
        lines += [
            "import lombok.*;",
            f"import {persistence_pkg}.*;",
        ]

    elif layer == "repository":
        lines += [
            "import org.springframework.stereotype.Repository;",
            "import org.springframework.data.jpa.repository.JpaRepository;",
        ]
        add_if_external(layer_pkgs['entity'], entity)

    elif layer == "service_interface":
        # interface only references domain types if needed (not here)
        lines += [
            "import java.util.List;",
        ]
        add_if_external(layer_pkgs['entity'], entity)

    elif layer == "service_impl":
        lines += [
            "import java.util.List;",
            "import org.springframework.beans.factory.annotation.Autowired;",
            "import org.springframework.stereotype.Service;",
        ]
        add_if_external(layer_pkgs['entity'], entity)
        add_if_external(layer_pkgs['repository'], f"{entity}Repository")
        add_if_external(layer_pkgs['service'], f"{entity}Service")

    elif layer == "controller":
        lines += [
            "import java.util.List;",
            "import org.springframework.beans.factory.annotation.Autowired;",
            "import org.springframework.web.bind.annotation.*;",
        ]
        add_if_external(layer_pkgs['entity'], entity)
        add_if_external(layer_pkgs['service'], f"{entity}Service")

    return "\n".join(lines) + "\n"


# -------------------- CODE GENERATORS --------------------
def gen_entity(base_pkg, entity, layer_pkgs, config):
    return f"""{gen_imports(base_pkg, entity, "entity", layer_pkgs, config)}
@Entity
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class {entity} {{
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
}}
"""

def gen_repo(base_pkg, entity, layer_pkgs, config):
    return f"""{gen_imports(base_pkg, entity, "repository", layer_pkgs, config)}
@Repository
public interface {entity}Repository extends JpaRepository<{entity}, Long> {{}}
"""

def gen_service_interface(base_pkg, entity, layer_pkgs, config):
    return f"""{gen_imports(base_pkg, entity, "service_interface", layer_pkgs, config)}
public interface {entity}Service {{

    List<{entity}> getAll();

    {entity} getById(Long id);

    {entity} save({entity} e);

    void delete(Long id);
}}
"""

def gen_service_impl(base_pkg, entity, layer_pkgs, config):
    return f"""{gen_imports(base_pkg, entity, "service_impl", layer_pkgs, config)}
@Service
public class {entity}ServiceImpl implements {entity}Service {{

    @Autowired
    private {entity}Repository repository;

    @Override
    public List<{entity}> getAll() {{ return null; }}

    @Override
    public {entity} getById(Long id) {{ return null; }}

    @Override
    public {entity} save({entity} e) {{ return null; }}

    @Override
    public void delete(Long id) {{ return; }}
}}
    """
    
def gen_service(base_pkg, entity, layer_pkgs, config):
    return gen_service_interface(base_pkg, entity, layer_pkgs, config)


def gen_controller(base_pkg, entity, layer_pkgs, config):
    lower = entity[0].lower() + entity[1:]
    return f"""{gen_imports(base_pkg, entity, "controller", layer_pkgs, config)}
@RestController
@RequestMapping("/api/{lower}s")
public class {entity}Controller {{

    @Autowired
    private {entity}Service service;

    @GetMapping
    public List<{entity}> getAll() {{ return service.getAll(); }}

    @GetMapping("/{{id}}")
    public {entity} getById(@PathVariable Long id) {{ return service.getById(id); }}

    @PostMapping
    public {entity} create(@RequestBody {entity} e) {{ return service.save(e); }}

    @PutMapping("/{{id}}")
    public {entity} update(@PathVariable Long id, @RequestBody {entity} e) {{
        e.setId(id);
        return service.save(e);
    }}

    @DeleteMapping("/{{id}}")
    public void delete(@PathVariable Long id) {{ service.delete(id); }}
}}
"""
    

GENERATORS = {
    "entity": gen_entity,
    "repository": gen_repo,
    "service": gen_service,
    "service_impl": gen_service_impl,
    "controller": gen_controller
}

# -------------------- MAIN --------------------
def main():
    print_banner()
    config = load_config()

    parser = argparse.ArgumentParser(description="Spring Boot CRUD generator")
    parser.add_argument("entities", nargs="*", help="Entity names (optional)")
    parser.add_argument("--single-folder", type=str, help="Put all files inside a single folder under the base package")
    parser.add_argument("--config", action="store_true", help="Edit settings (base_package, folders, persistence_package)")
    args = parser.parse_args()

    if args.config:
        print(json.dumps(config, indent=4))
        if ask_yes_no("Do you want to modify settings?", "n"):
            # base package
            new_bp = input(f"base_package [{config.get('base_package','')}]: ").strip()
            if new_bp:
                config["base_package"] = new_bp
            # persistence package
            pp = config.get("persistence_package", "auto")
            new_pp = input(f"persistence_package (jakarta.persistence / javax.persistence / auto) [{pp}]: ").strip()
            if new_pp:
                config["persistence_package"] = new_pp
            # folder names
            for k, v in config["folders"].items():
                new_v = input(f"{k} folder name [{v}]: ").strip()
                if new_v:
                    config["folders"][k] = new_v
            save_config(config)
            print(colored("✅ Config updated successfully!", "green"))
        return

    # Entities
    if not args.entities:
        entities_input = input("Enter entity names (comma-separated): ")
        entities = [e.strip() for e in entities_input.split(",") if e.strip()]
    else:
        entities = args.entities

    if not entities:
        print("❌ You must provide at least one entity name.")
        sys.exit(1)

    # Base package is ONLY from config (no auto-detect)
    base_pkg_root = config["base_package"]

    # Single-folder support
    if args.single_folder:
        single_folder = args.single_folder.strip()
        base_pkg_used = f"{base_pkg_root}.{single_folder}"
        print(colored(f"\n📦 Using single-folder mode: {base_pkg_used}", "cyan"))
        layer_pkgs = {layer: base_pkg_used for layer in ["entity", "repository", "service", "controller"]}
        layer_pkgs["service_impl"] = base_pkg_used
    else:
        base_pkg_used = base_pkg_root
        print(colored(f"\n📦 Using base package from config: {base_pkg_used}", "cyan"))
        layer_pkgs = {
            "entity": f"{base_pkg_used}.{config['folders']['entity']}",
            "repository": f"{base_pkg_used}.{config['folders']['repository']}",
            "service": f"{base_pkg_used}.{config['folders']['service']}",
            "controller": f"{base_pkg_used}.{config['folders']['controller']}",
        }
        layer_pkgs["service_impl"] = f"{layer_pkgs['service']}.impl"

    # Ensure folder structure exists
    for pkg in set(layer_pkgs.values()):
        pkg_path = os.path.join(BASE_SRC, pkg.replace(".", "/"))
        ensure_dir(pkg_path)

    # Layers to generate
    print("\nEntity layer is mandatory and will be generated for all entities.")
    layers_to_generate = ["entity"]

    # Repository?
    if ask_yes_no(f"Do you want to generate Repository layer for all entities?"):
        layers_to_generate.append("repository")

    # Service? (interface + impl together)
    if ask_yes_no(f"Do you want to generate Service layer (interface + impl) for all entities?"):
        layers_to_generate.append("service")
        layers_to_generate.append("service_impl")

    # Controller?
    if ask_yes_no(f"Do you want to generate Controller layer for all entities?"):
        layers_to_generate.append("controller")

    # Generate files
    for entity in entities:
        print(f"\n🔹 Generating for entity: {entity}")
        for layer in layers_to_generate:
            pkg = layer_pkgs[layer]
            base_path = os.path.join(BASE_SRC, pkg.replace(".", "/"))
            filename = f"{entity}.java" if layer == "entity" else (f"{entity}ServiceImpl.java" 
                                                                   if layer=="service_impl" 
                                                                   else f"{entity}{layer.capitalize()}.java")
            content = GENERATORS[layer](pkg, entity, layer_pkgs, config)
            path = os.path.join(base_path, filename)
            write_file(path, content)

    print("\n🎉 CRUD boilerplate generation complete!")

if __name__ == "__main__":
    main()
