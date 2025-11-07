function confirmDeployRules() {
  showDeleteModal("Voulez-vous vraiment déployer les règles ?", function() {
    saveRules();
  }, "Déployer", "var(--color-success)");
}

async function saveRules() {
  localStorage.setItem("metadidomi_cloud_rules", JSON.stringify(rules));
  // Regrouper les règles par collection et actions
  const grouped = {};
  rules.forEach(rule => {
    if (!grouped[rule.collection]) grouped[rule.collection] = {collection: rule.collection};
    grouped[rule.collection][rule.action] = rule.condition;
  });
  const rulesToSend = Object.values(grouped);
  await fetch("/sync_metadidomi_cloud_rules", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(rulesToSend)
  });
  showSnackbar("Règles déployées !", "var(--color-success)");
  setDeployDirty(false);
}

// Section switching logic
function setActiveMenuBtn(btnId) {
  document.querySelectorAll('.menu-btn').forEach(btn => btn.classList.remove('active'));
  const btn = document.getElementById(btnId);
  if (btn) btn.classList.add('active');
}
if (document.getElementById('btn-db')) {
  document.getElementById('btn-db').onclick = function() {
    if (document.getElementById('db-section')) document.getElementById('db-section').style.display = '';
    if (document.getElementById('rules-section')) document.getElementById('rules-section').style.display = 'none';
    if (document.getElementById('users-section')) document.getElementById('users-section').style.display = 'none';
    setActiveMenuBtn('btn-db');
  };
}
if (document.getElementById('btn-rules')) {
  document.getElementById('btn-rules').onclick = function() {
    if (document.getElementById('db-section')) document.getElementById('db-section').style.display = 'none';
    if (document.getElementById('rules-section')) document.getElementById('rules-section').style.display = '';
    if (document.getElementById('users-section')) document.getElementById('users-section').style.display = 'none';
    setActiveMenuBtn('btn-rules');
  };
}
if (document.getElementById('btn-users')) {
  document.getElementById('btn-users').onclick = function() {
    const url = `http://${window.location.hostname}:5300/users_list`;
    window.open(url, '_blank');
  };
}
window.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('db-section')) document.getElementById('db-section').style.display = '';
  if (document.getElementById('rules-section')) document.getElementById('rules-section').style.display = 'none';
  if (document.getElementById('users-section')) document.getElementById('users-section').style.display = 'none';
  setActiveMenuBtn('btn-db');
});

let rulesDirty = false;

function setDeployDirty(isDirty) {
  rulesDirty = isDirty;
  const btn = document.querySelector("#rules-section button[onclick*='confirmDeployRules']");
  if (btn) {
    if (isDirty) {
      btn.style.background = '#e74c3c';
      btn.style.color = '#fff';
      btn.title = 'Des modifications non déployées sont présentes';
    } else {
      btn.style.background = 'var(--primary)';
      btn.style.color = 'var(--menu-btn-active-color)';
      btn.title = '';
    }
  }
}

function markRulesDirty() {
  setDeployDirty(true);
}

// Après chargement initial des règles, on remet le bouton à l'état normal
async function loadRules() {
  const res = await fetch("/rules");
  const data = await res.json();
  rules = [];
  data.forEach(rule => {
    // Pour chaque action, créer une entrée pour le tableau dynamique
    ["create", "read", "write", "delete"].forEach(action => {
      rules.push({
        collection: rule.collection,
        action: action,
        condition: rule[action]
      });
    });
  });
  renderRulesTable();
  setDeployDirty(false); // <-- Ajouté ici pour corriger le bug
}

loadRules();

// --- Tableau des règles style FlutterFlow ---
function renderRulesTable() {
  const table = document.getElementById("rules-table");
  table.innerHTML = "";
  // Regroupe les règles par collection
  const collections = {};
  rules.forEach((rule, i) => {
    if (!collections[rule.collection]) collections[rule.collection] = {};
    collections[rule.collection][rule.action] = {condition: rule.condition, index: i};
  });
  Object.keys(collections).forEach(colName => {
    table.insertAdjacentHTML("beforeend", `
      <tr class="bg-gray-900">
        <td class="p-2 font-bold">${colName}</td>
        <td class="p-2">${renderRuleCell(collections[colName], 'create')}</td>
        <td class="p-2">${renderRuleCell(collections[colName], 'read')}</td>
        <td class="p-2">${renderRuleCell(collections[colName], 'write')}</td>
        <td class="p-2">${renderRuleCell(collections[colName], 'delete')}</td>
        <td class="p-2 text-center">
          <button onclick="deleteCollectionRules('${colName}')" style="color:var(--color-danger);background:none;border:none;font-size:1.2em;cursor:pointer;">🗑</button>
        </td>
      </tr>
    `);
  });
}
function renderRuleCell(colObj, action) {
  if (!colObj[action]) return `<span style='color:var(--color-text-muted);'>—</span>`;
  const cond = colObj[action].condition;
  const idx = colObj[action].index;
  return `<select class='border rounded-lg p-1 w-full' onchange='updateRule(${idx}, "condition", this.value)'>
    <option value="true" ${cond==="true"?"selected":""}>Toujours autorisé</option>
    <option value="false" ${cond==="false"?"selected":""}>Toujours refusé</option>
    <option value="auth != null" ${cond==="auth != null"?"selected":""}>Utilisateur connecté</option>
    <option value="auth.uid == resource.id" ${cond==="auth.uid == resource.id"?"selected":""}>Utilisateur propriétaire</option>
  </select>`;
}
function deleteCollectionRules(colName) {
  rules = rules.filter(r => r.collection !== colName);
  renderRulesTable();
  markRulesDirty();
}

// --- Gestion des règles ---
let rules = [];
function addRule() {
  const rowIndex = rules.length;
  rules.push({collection: "", action: "read", condition: "auth != null"});
  renderRulesTable();
  markRulesDirty();
}
function updateRule(index, key, value) {
  rules[index][key] = value;
}
function deleteRule(index) {
  rules.splice(index, 1);
  renderRulesTable();
  markRulesDirty();
}
function simulateRule() {
  const collection = document.getElementById("sim-collection").value;
  const action = document.getElementById("sim-action").value;
  let auth = {uid: document.getElementById("sim-auth").value || null};
  if (currentUser && !auth.uid) auth.uid = currentUser.email;
  const resource = {id: "user123"}; // Exemple
  const rule = rules.find(r => r.collection === collection && r.action === action);
  if (!rule) {
    document.getElementById("sim-result").innerText = "❌ Aucune règle trouvée";
    return;
  }
  let result = false;
  try {
    result = eval(rule.condition.replace("auth", JSON.stringify(auth)).replace("resource", JSON.stringify(resource)));
  } catch (e) {
    result = false;
  }
  document.getElementById("sim-result").innerText = result ? "✅ Autorisé" : "⛔ Refusé";
}
renderRulesTable();

async function autoFillRulesFromDatabase() {
  const res = await fetch("/get_metadidomi_cloud_database");
  const db = await res.json();
  const collections = Object.keys(db);
  // Pour chaque collection, s'assurer qu'il y a une règle pour chaque action
  collections.forEach(col => {
    ["create", "read", "write", "delete"].forEach(action => {
      if (!rules.find(r => r.collection === col && r.action === action)) {
        rules.push({collection: col, action: action, condition: "auth != null"});
      }
    });
  });
  renderRulesTable();
  setDeployDirty(false); // <-- Ajouté ici aussi
}
window.addEventListener('DOMContentLoaded', autoFillRulesFromDatabase);

// --- Simulateur : remplir le dropdown des collections dynamiquement ---
async function fillSimCollectionsDropdown() {
  const res = await fetch("/get_metadidomi_cloud_database");
  const db = await res.json();
  const select = document.getElementById("sim-collection");
  if (!select) return;
  select.innerHTML = "";
  Object.keys(db).forEach(col => {
    const opt = document.createElement("option");
    opt.value = col;
    opt.textContent = col;
    select.appendChild(opt);
  });
}
window.addEventListener('DOMContentLoaded', fillSimCollectionsDropdown);

let metadidomiCloudDatabase = JSON.parse(localStorage.getItem("metadidomi_cloud_database_complete")) || {};
let currentPath = [];
let history = [];
let historyIndex = -1;
let selectedItem = null;

// --- Affichage du statut de synchronisation ---
function checkSyncStatus() {
  fetch("/get_metadidomi_cloud_database")
    .then(r => r.json())
    .then(data => {
      const local = JSON.stringify(metadidomiCloudDatabase);
      const remote = JSON.stringify(data);
      const statusDiv = document.getElementById("sync-status");
      const isSynced = local === remote;
      if (isSynced) {
        statusDiv.textContent = "Données synchronisées avec la base";
        statusDiv.style.color = "var(--color-success)";
      } else {
        statusDiv.textContent = "Données non synchronisées avec la base";
        statusDiv.style.color = "var(--color-danger)";
      }
      updateSyncStatusText(isSynced);
      showRulesCodeMirror(data);
    })
    .catch(() => {
      const statusDiv = document.getElementById("sync-status");
      statusDiv.textContent = "Impossible de vérifier la synchronisation";
      statusDiv.style.color = "var(--color-warning)";
      updateSyncStatusText(false);
    });
}

// Appel au chargement et après chaque sauvegarde
window.addEventListener('DOMContentLoaded', checkSyncStatus);

// --- Snackbar ---
function showSnackbar(message, color = "var(--color-success)") {
  let snackbar = document.getElementById("snackbar");
  if (!snackbar) {
    snackbar = document.createElement("div");
    snackbar.id = "snackbar";
    snackbar.style.position = "fixed";
    snackbar.style.left = "50%";
    snackbar.style.bottom = "30px";
    snackbar.style.transform = "translateX(-50%)";
    snackbar.style.background = color;
    snackbar.style.color = "var(--color-text-inverse)";
    snackbar.style.padding = "14px 32px";
    snackbar.style.borderRadius = "8px";
    snackbar.style.fontSize = "1.1em";
    snackbar.style.boxShadow = "0 2px 8px var(--color-shadow)";
    snackbar.style.zIndex = 9999;
    snackbar.style.opacity = 0;
    snackbar.style.transition = "opacity 0.3s";
    document.body.appendChild(snackbar);
  }
  snackbar.textContent = message;
  snackbar.style.opacity = 1;
  setTimeout(() => { snackbar.style.opacity = 0; }, 2000);
}

// --- Utils ---
save = function(auto = false) {
  localStorage.setItem("metadidomi_cloud_database_complete", JSON.stringify(metadidomiCloudDatabase));
  fetch("/sync_metadidomi_cloud_database", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(metadidomiCloudDatabase)
  }).then(()=>{
    render();
    checkSyncStatus();
    if (!auto) showSnackbar("Sauvegarde réussie !", "var(--color-success)");
  });
}
function getCurrentLevel(){ let ref = metadidomiCloudDatabase; for(let key of currentPath) ref = ref[key]; return ref; }
function generateId(length=20){ const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'; let id=''; for(let i=0;i<length;i++) id+=chars.charAt(Math.floor(Math.random()*chars.length)); return id; }
function getAllDocumentPaths(obj, prefix=""){ let paths=[]; for(let k in obj){ if(obj[k].fields !== undefined && obj[k].subCollections !== undefined){ paths.push(prefix+k); for(let subCol in obj[k].subCollections){ paths=paths.concat(getAllDocumentPaths(obj[k].subCollections[subCol], prefix+k+"/subCollections/"+subCol+"/")); } } } return paths; }

// --- Navigation ---
function goTo(path){ currentPath = path.slice(); history = history.slice(0, historyIndex + 1); history.push(currentPath.slice()); historyIndex++; render(); }
function goBack(){ if(historyIndex>0){ historyIndex--; currentPath=history[historyIndex].slice(); render(); } }
function goNext(){ if(historyIndex < history.length-1){ historyIndex++; currentPath=history[historyIndex].slice(); render(); } }

// --- Breadcrumb & nav buttons ---
function renderBreadcrumb(){
  const breadcrumb=document.getElementById("breadcrumb"); breadcrumb.innerHTML="";
  if(currentPath.length===0){ breadcrumb.textContent="Racine"; return; }
  let pathSoFar=[]; currentPath.forEach((key,i)=>{ if(i>0) breadcrumb.innerHTML+=" / "; pathSoFar.push(key); const span=document.createElement("span"); span.textContent=key; span.onclick=()=>{ goTo(pathSoFar.slice()); }; breadcrumb.appendChild(span); });
}
function updateNavButtons(){ document.querySelector("#fields button:nth-child(1)").disabled = historyIndex <= 0; document.querySelector("#fields button:nth-child(2)").disabled = historyIndex >= history.length - 1; }

// --- Sélection ---
function selectItem(checkbox, type, name){
  if(checkbox.checked){
    if(selectedItem && selectedItem.checkbox !== checkbox) selectedItem.checkbox.checked = false;
    selectedItem = {type, name, checkbox};
    document.getElementById(type==="collection"?"deleteBtn":"deleteDocBtn").style.display="inline-block";
  } else {
    selectedItem = null;
    document.getElementById("deleteBtn").style.display="none";
    document.getElementById("deleteDocBtn").style.display="none";
  }
}

// --- Suppression ---
// --- Modale de confirmation suppression ---
function showDeleteModal(message, onConfirm, confirmLabel = "Supprimer", confirmColor = "var(--color-danger)") {
  let modal = document.getElementById('delete-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'delete-modal';
    modal.style.position = 'fixed';
    modal.style.top = 0;
    modal.style.left = 0;
    modal.style.width = '100vw';
    modal.style.height = '100vh';
    modal.style.background = 'var(--color-modal-bg)';
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.zIndex = 10000;
    modal.innerHTML = `
      <div style="background:var(--color-bg-panel);padding:32px 28px 22px 28px;border-radius:12px;box-shadow:0 4px 24px var(--color-shadow);min-width:320px;max-width:90vw;text-align:center;">
        <div id="modal-message" style="font-size:1.15em;margin-bottom:18px;">${message}</div>
        <button id="modal-confirm-btn" style="background:${confirmColor};color:var(--color-text-inverse);padding:8px 22px;border:none;border-radius:6px;font-size:1em;font-weight:bold;margin-right:12px;cursor:pointer;">${confirmLabel}</button>
        <button id="modal-cancel-btn" style="background:var(--color-cancel-bg);color:var(--color-cancel-text);padding:8px 22px;border:none;border-radius:6px;font-size:1em;cursor:pointer;">Annuler</button>
      </div>
    `;
    document.body.appendChild(modal);
  } else {
    let msgDiv = modal.querySelector('#modal-message');
    if (msgDiv) msgDiv.textContent = message;
    else modal.querySelector('div').firstChild.textContent = message;
    let confirmBtn = modal.querySelector('#modal-confirm-btn');
    if (confirmBtn) {
      confirmBtn.textContent = confirmLabel;
      confirmBtn.style.background = confirmColor;
    }
    modal.style.display = 'flex';
  }
  document.getElementById('modal-confirm-btn').onclick = function() {
    modal.style.display = 'none';
    onConfirm();
  };
  document.getElementById('modal-cancel-btn').onclick = function() {
    modal.style.display = 'none';
  };
}

function deleteCollectionRecursively(colName){
  // Appel à l'API backend pour supprimer la collection et ses règles
  fetch(`/metadidomi_cloud_database/${encodeURIComponent(colName)}`, {method: 'DELETE'})
    .then(res => {
      if (!res.ok) throw new Error('Erreur lors de la suppression de la collection');
      // Suppression locale pour cohérence immédiate
      if(metadidomiCloudDatabase[colName]) delete metadidomiCloudDatabase[colName];
      showSnackbar(`Collection "${colName}" et ses règles supprimées.`, 'var(--color-success)');
      save();
      loadRules();
      fillSimCollectionsDropdown();
      render();
    })
    .catch(err => {
      showSnackbar('Erreur lors de la suppression de la collection', 'var(--color-danger)');
    });
  markRulesDirty();
}
function deleteDocumentRecursively(docRef, docName){
  if(!docRef[docName]) return;
  const doc = docRef[docName];
  if(doc.subCollections){
    for(let subCol in doc.subCollections){
      for(let subDoc in doc.subCollections[subCol]){
        deleteDocumentRecursively(doc.subCollections[subCol], subDoc);
      }
    }
  }
  if(doc.fields){ for(let field in doc.fields){ delete doc.fields[field]; } }
  delete docRef[docName];
}
function deleteSelected(){
  if(!selectedItem) return;
  showDeleteModal(`Voulez-vous vraiment supprimer ${selectedItem.type} "${selectedItem.name}" ?`, function() {
    if(selectedItem.type === "collection") deleteCollectionRecursively(selectedItem.name);
    else if(selectedItem.type === "document") deleteDocumentRecursively(getCurrentLevel(), selectedItem.name);
    history = []; historyIndex = -1; currentPath = [];
    selectedItem = null;
    document.getElementById("deleteBtn").style.display="none";
    document.getElementById("deleteDocBtn").style.display="none";
    save();
  });
}

// --- Champs ---
function renderField(fieldName, fieldData, container, parentObj){
  let div=document.createElement("div"); div.className="subfield";
  let nameSpan=document.createElement("span"); nameSpan.textContent=fieldName+" "; div.appendChild(nameSpan);

  let typeSelect=document.createElement("select");
  ["string","number","boolean","timestamp","map","array","null","reference","geopoint","color","double","imagePath","videoPath","audioPath"].forEach(t=>{
    let opt=document.createElement("option"); opt.value=t; opt.textContent=t; if(fieldData.type===t) opt.selected=true; typeSelect.appendChild(opt);
  });
  typeSelect.onchange=(e)=>{ 
    fieldData.type=e.target.value; 
    if(e.target.value==="map") fieldData.value={};
    if(e.target.value==="array") fieldData.value=[];
    if(e.target.value==="timestamp") fieldData.value="";
    if(e.target.value==="reference") fieldData.value="";
    if(e.target.value==="geopoint") fieldData.value={latitude:0, longitude:0};
    if(e.target.value==="number") fieldData.value=0;
    if(e.target.value==="double") fieldData.value=0.0;
    if(e.target.value==="boolean") fieldData.value=false;
    if(e.target.value==="string") fieldData.value="";
    if(e.target.value==="color") fieldData.value="#000000";
    if(e.target.value==="imagePath"||e.target.value==="videoPath"||e.target.value==="audioPath") fieldData.value="";
    if(e.target.value==="null") fieldData.value=null;
    save(true); 
  };
  div.appendChild(typeSelect);

  if(fieldData.type==="string"){
    let input=document.createElement("input"); input.type="text"; input.value=fieldData.value||""; input.onchange=(e)=>{ fieldData.value=e.target.value; save(true); }; div.appendChild(input);
  }
  else if(fieldData.type==="number"){
    let input=document.createElement("input"); input.type="number"; input.value=fieldData.value||0; input.onchange=(e)=>{ fieldData.value=parseFloat(e.target.value)||0; save(true); }; div.appendChild(input);
  }
  else if(fieldData.type==="double"){
    let input=document.createElement("input"); input.type="number"; input.step="any"; input.value=fieldData.value||0.0; input.onchange=(e)=>{ fieldData.value=parseFloat(e.target.value)||0.0; save(true); }; div.appendChild(input);
  }
  else if(fieldData.type==="color"){
    let input=document.createElement("input"); input.type="color"; input.value=fieldData.value||"#000000"; input.onchange=(e)=>{ fieldData.value=e.target.value; save(true); }; div.appendChild(input);
  }
  else if(fieldData.type==="imagePath"){
    let input=document.createElement("input"); input.type="text"; input.value=fieldData.value||""; input.placeholder="Chemin ou URL de l'image"; input.onchange=(e)=>{ fieldData.value=e.target.value; save(true); }; div.appendChild(input);
    if(fieldData.value){ let img=document.createElement("img"); img.src=fieldData.value; img.style.maxWidth="120px"; img.style.maxHeight="80px"; img.style.marginLeft="8px"; div.appendChild(img); }
  }
  else if(fieldData.type==="videoPath"){
    let input=document.createElement("input"); input.type="text"; input.value=fieldData.value||""; input.placeholder="Chemin ou URL de la vidéo"; input.onchange=(e)=>{ fieldData.value=e.target.value; save(true); }; div.appendChild(input);
    if(fieldData.value){ let video=document.createElement("video"); video.src=fieldData.value; video.controls=true; video.style.maxWidth="120px"; video.style.maxHeight="80px"; video.style.marginLeft="8px"; div.appendChild(video); }
  }
  else if(fieldData.type==="audioPath"){
    let input=document.createElement("input"); input.type="text"; input.value=fieldData.value||""; input.placeholder="Chemin ou URL de l'audio"; input.onchange=(e)=>{ fieldData.value=e.target.value; save(true); }; div.appendChild(input);
    if(fieldData.value){ let audio=document.createElement("audio"); audio.src=fieldData.value; audio.controls=true; audio.style.marginLeft="8px"; div.appendChild(audio); }
  }
  else if(fieldData.type==="boolean"){
    let select=document.createElement("select"); ["true","false"].forEach(val=>{ let opt=document.createElement("option"); opt.value=val; opt.textContent=val; if(String(fieldData.value)===val) opt.selected=true; select.appendChild(opt); });
    select.onchange=(e)=>{ fieldData.value=(e.target.value==="true"); save(true); }; div.appendChild(select);
  }
  else if(fieldData.type==="null"){
    let span=document.createElement("span"); span.textContent="null"; fieldData.value=null; div.appendChild(span);
  }
  else if(fieldData.type==="timestamp"){
    let input=document.createElement("input"); input.type="datetime-local"; input.value=fieldData.value||""; input.onchange=(e)=>{ fieldData.value=e.target.value; save(true); }; div.appendChild(input);
  }
  else if(fieldData.type==="reference"){
    let select=document.createElement("select"); select.innerHTML="<option value=''>--choisir document--</option>";
    function getAllDocs(obj, prefix=""){
      let docs=[];
      for(let k in obj){
        if(obj[k] && typeof obj[k]==="object" && obj[k].fields!==undefined && obj[k].subCollections!==undefined){
          docs.push((prefix ? prefix+"/" : "")+k);
          for(let subCol in obj[k].subCollections){
            docs=docs.concat(getAllDocs(obj[k].subCollections[subCol], (prefix ? prefix+"/" : "")+k+"/subCollections/"+subCol));
          }
        }
      }
      return docs;
    }
    let allDocs = [];
    for(let col in metadidomiCloudDatabase) {
      allDocs = allDocs.concat(getAllDocs(metadidomiCloudDatabase[col], col));
    }
    allDocs.forEach(d=>{ let opt=document.createElement("option"); opt.value=d; opt.textContent=d; if(fieldData.value===d) opt.selected=true; select.appendChild(opt); });
    select.onchange=(e)=>{ fieldData.value=e.target.value; save(true); };
    div.appendChild(select);
  }
  else if(fieldData.type==="geopoint"){
    let lat=document.createElement("input"); lat.type="number"; lat.step="any"; lat.placeholder="Latitude"; lat.value=fieldData.value.latitude||0; lat.onchange=(e)=>{ fieldData.value.latitude=parseFloat(e.target.value)||0; save(true); };
    let lng=document.createElement("input"); lng.type="number"; lng.step="any"; lng.placeholder="Longitude"; lng.value=fieldData.value.longitude||0; lng.onchange=(e)=>{ fieldData.value.longitude=parseFloat(e.target.value)||0; save(true); }; div.appendChild(lat); div.appendChild(lng);
  }
  else if(fieldData.type==="map"){
    let valDiv=document.createElement("div");
    for(let k in fieldData.value) renderField(k, fieldData.value[k], valDiv, fieldData.value);
    let addBtn=document.createElement("button"); addBtn.textContent="Ajouter sous-champ"; addBtn.onclick=()=>{ let newKey=prompt("Nom du sous-champ:"); if(!newKey) return; fieldData.value[newKey]={type:"string", value:""}; save(true); }; valDiv.appendChild(addBtn); div.appendChild(valDiv);
  }
  else if(fieldData.type==="array"){
    let valDiv=document.createElement("div");
    fieldData.value.forEach((v,i)=>{
      let elemDiv=document.createElement("div"); elemDiv.className="subfield";
      renderField("["+i+"]", v, elemDiv, fieldData.value);
      let del=document.createElement("span"); del.textContent="❌"; del.className="delete-btn";
      del.onclick=()=>{
        showDeleteModal(`Voulez-vous vraiment supprimer l'élément d'array à l'index ${i} ?`, function() {
          fieldData.value.splice(i,1); save(true);
        });
      };
      elemDiv.appendChild(del);
      valDiv.appendChild(elemDiv);
    });
    let addBtn=document.createElement("button"); addBtn.textContent="Ajouter élément"; addBtn.onclick=()=>{ fieldData.value.push({type:"string", value:""}); save(true); }; valDiv.appendChild(addBtn);
  }

  let del=document.createElement("span"); del.textContent=" ❌"; del.className="delete-btn"; del.onclick=()=>{
    showDeleteModal(`Voulez-vous vraiment supprimer \"${fieldName}\" ?`, function() {
      delete parentObj[fieldName];
      save(true);
    });
  };
  div.appendChild(del);
  container.appendChild(div);
}

// --- Rendu principal ---
function render(){
  renderBreadcrumb(); updateNavButtons();
  const colList=document.getElementById("collectionList"); colList.innerHTML="";
  for(let col in metadidomiCloudDatabase){
    let li=document.createElement("li");
    let cb=document.createElement("input"); cb.type="checkbox"; cb.onchange=()=>selectItem(cb,"collection",col); li.appendChild(cb);
    let span=document.createElement("span"); span.textContent=" "+col; li.appendChild(span);
    // Affichage date de création si présente
    if(metadidomiCloudDatabase[col]._createdAt){
      let dateSpan = document.createElement("span");
      dateSpan.textContent = " (créée le " + new Date(metadidomiCloudDatabase[col]._createdAt).toLocaleDateString('fr-FR') + ")";
      dateSpan.style.fontSize = "0.92em";
      dateSpan.style.color = "#888";
      li.appendChild(dateSpan);
    }
    // Ajout icône SVG suppression collection
    let del=document.createElement("span");
    del.innerHTML = `<svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='red' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle;cursor:pointer;'><polyline points='3 6 5 6 21 6'></polyline><path d='M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m5 0V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2'></path><line x1='10' y1='11' x2='10' y2='17'></line><line x1='14' y1='11' x2='14' y2='17'></line></svg>`;
    del.title = "Supprimer la collection";
    del.onclick = (e) => {
      e.stopPropagation();
      showDeleteModal(`Voulez-vous vraiment supprimer la collection "${col}" et ses règles ?`, function() {
        deleteCollectionRecursively(col);
        selectedItem = null;
        document.getElementById("deleteBtn").style.display="none";
      });
    };
    li.appendChild(del);
    if(currentPath[0]===col) li.classList.add("selected");
    li.onclick=(e)=>{ if(e.target.tagName!=="INPUT" && e.target.tagName!=='svg' && e.target.tagName!=='path') goTo([col]); };
    colList.appendChild(li);
  }
  const docList=document.getElementById("documentList"); docList.innerHTML="";
  if(currentPath.length>=1){
    let colRef = metadidomiCloudDatabase[currentPath[0]];
    if(currentPath.length>2 && currentPath[1]==="subCollections") colRef = getCurrentLevel();
    for(let doc in colRef){
      let li=document.createElement("li");
      let cb=document.createElement("input"); cb.type="checkbox"; cb.onchange=()=>selectItem(cb,"document",doc); li.appendChild(cb);
      let span=document.createElement("span"); span.textContent=" "+doc; li.appendChild(span);
      // Ajout icône SVG suppression document
      let del=document.createElement("span");
      del.innerHTML = `<svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='red' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle;cursor:pointer;'><polyline points='3 6 5 6 21 6'></polyline><path d='M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m5 0V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2'></path><line x1='10' y1='11' x2='10' y2='17'></line><line x1='14' y1='11' x2='14' y2='17'></line></svg>`;
      del.title = "Supprimer le document";
      del.onclick = (e) => {
        e.stopPropagation();
        showDeleteModal(`Voulez-vous vraiment supprimer le document "${doc}" ?`, function() {
          deleteDocumentRecursively(colRef, doc);
          selectedItem = null;
          document.getElementById("deleteDocBtn").style.display="none";
          save();
          render();
        });
      };
      li.appendChild(del);
      if(currentPath[1]===doc) li.classList.add("selected");
      li.onclick=(e)=>{ if(e.target.tagName!=="INPUT" && e.target.tagName!=='svg' && e.target.tagName!=='path') goTo([currentPath[0],doc]); };
      docList.appendChild(li);
    }
  }
  const fieldsContainer=document.getElementById("fieldsContainer"); fieldsContainer.innerHTML=""; const subCollectionsDiv=document.getElementById("subCollections"); subCollectionsDiv.innerHTML="";
  if(currentPath.length%2===0 && currentPath.length>=2){ let docRef=getCurrentLevel(); for(let k in docRef.fields || {}) renderField(k, docRef.fields[k], fieldsContainer, docRef.fields); for(let subCol in docRef.subCollections || {}){ let div=document.createElement("div"); div.className="nested"; div.textContent="📂 "+subCol; div.onclick=()=>{ goTo([...currentPath,"subCollections",subCol]); }; subCollectionsDiv.appendChild(div); } }
  updateToolbarInfo();
}

// --- Add operations ---
function addCollection(){
  const name=document.getElementById("newCollectionName").value.trim();
  if(!name) return;
  if(metadidomiCloudDatabase[name]) { alert("Cette collection existe déjà !"); return; }
  metadidomiCloudDatabase[name]={ _createdAt: new Date().toISOString() };
  document.getElementById("newCollectionName").value="";
  save();
  markRulesDirty();
}
function addDocument(){ if(currentPath.length!==1 && currentPath.slice(-2)[0]!=="subCollections") return alert("Choisis une collection !"); let id=document.getElementById("newDocumentId").value.trim(); if(!id) id=generateId(); let colRef=getCurrentLevel(); if(colRef[id]) { alert("Ce document existe déjà !"); return; } colRef[id]={fields:{}, subCollections:{}}; document.getElementById("newDocumentId").value=""; save(); }
function addField(){ if(currentPath.length%2!==0 || currentPath.length<2) return alert("Choisis un document !"); const name=prompt("Nom du champ:"); if(!name) return; let docRef=getCurrentLevel(); if(!docRef.fields) docRef.fields={}; if(docRef.fields[name]) { alert("Ce champ existe déjà !"); return; } docRef.fields[name]={type:"string", value:""}; save(); }
function addSubCollection(){ if(currentPath.length%2!==0 || currentPath.length<2) return alert("Choisis un document !"); const name=prompt("Nom sous-collection:"); if(!name) return; let docRef=getCurrentLevel(); if(!docRef.subCollections) docRef.subCollections={}; if(docRef.subCollections[name]) { alert("Cette sous-collection existe déjà !"); return; } docRef.subCollections[name]={}; save(); }

// --- Toolbar info ---
function updateToolbarInfo() {
  const info = document.getElementById('toolbar-info');
  if (!info) return;
  let col = currentPath[0] ? `Collection: <b>${currentPath[0]}</b>` : '';
  let doc = currentPath[1] ? ` | Document: <b>${currentPath[1]}</b>` : '';
  info.innerHTML = col + doc;
}

// --- Ajout du texte de synchronisation devant Gestion des règles ---
function updateSyncStatusText(isSynced) {
  const h2 = document.querySelector('#rules-section h2');
  let syncText = document.getElementById('sync-status-text');
  if (!syncText) {
    syncText = document.createElement('span');
    syncText.id = 'sync-status-text';
    syncText.style.fontWeight = 'bold';
    syncText.style.marginRight = '14px';
    h2.prepend(syncText);
  }
  syncText.textContent = isSynced ? 'Synchronisé' : 'Non synchronisé';
  syncText.style.color = isSynced ? 'var(--color-success)' : 'var(--color-danger)';
}

// --- Suppression du bouton Ajouter une règle ---
const addRuleBtn = document.querySelector("#rules-section button[onclick*='addRule']");
if (addRuleBtn) addRuleBtn.remove();

// --- Ajout du SVG code qui ouvre une modale CodeMirror ---
function showRulesModal(rules) {
  let modal = document.getElementById('rules-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'rules-modal';
    modal.style.position = 'fixed';
    modal.style.top = 0;
    modal.style.left = 0;
    modal.style.width = '100vw';
    modal.style.height = '100vh';
    modal.style.background = 'var(--modal-bg)';
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.zIndex = 10000;
    modal.innerHTML = `
      <div style="background:var(--color-bg-panel);padding:32px 28px 22px 28px;border-radius:12px;box-shadow:0 4px 24px var(--color-shadow);min-width:420px;max-width:90vw;text-align:left;">
        <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;'>
          <span style='font-size:1.15em;font-weight:600;color:var(--color-primary);'>Règles de sécurité (lecture seule)</span>
          <button id='close-rules-modal' style='background:var(--color-cancel-bg);color:var(--color-cancel-text);padding:6px 18px;border:none;border-radius:6px;font-size:1em;cursor:pointer;'>Fermer</button>
        </div>
        <textarea id='rules-modal-codemirror' style='width:100%;height:320px;background:var(--input-bg);color:var(--input-text);border:1px solid var(--input-border);border-radius:8px;'></textarea>
      </div>
    `;
    document.body.appendChild(modal);
    document.getElementById('close-rules-modal').onclick = function() {
      modal.style.display = 'none';
    };
    // Chargement dynamique de CodeMirror si pas déjà présent
    if (!window.CodeMirror) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.css';
      document.head.appendChild(link);
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.js';
      script.onload = function() {
        const jsScript = document.createElement('script');
        jsScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/javascript/javascript.min.js';
        jsScript.onload = function() {
          window.rulesModalCM = CodeMirror.fromTextArea(document.getElementById('rules-modal-codemirror'), {
            lineNumbers: true,
            mode: 'application/json',
            readOnly: true,
            theme: document.documentElement.getAttribute('data-theme') === 'dark' ? 'material-darker' : 'default'
          });
          window.rulesModalCM.setValue(JSON.stringify(rules, null, 2));
        };
        document.body.appendChild(jsScript);
      };
      document.body.appendChild(script);
    } else {
      window.rulesModalCM = CodeMirror.fromTextArea(document.getElementById('rules-modal-codemirror'), {
        lineNumbers: true,
        mode: 'application/json',
        readOnly: true,
        theme: document.documentElement.getAttribute('data-theme') === 'dark' ? 'material-darker' : 'default'
      });
      window.rulesModalCM.setValue(JSON.stringify(rules, null, 2));
    }
  } else {
    modal.style.display = 'flex';
    if (window.rulesModalCM) window.rulesModalCM.setValue(JSON.stringify(rules, null, 2));
  }
}
function insertCodeSvgButton() {
  const deployBtn = document.querySelector("#rules-section button[onclick*='confirmDeployRules']");
  if (!document.getElementById('code-svg-btn')) {
    const div = document.createElement('div');
    div.style.marginTop = '8px';
    div.innerHTML = `<span id='code-svg-btn' style='cursor:pointer;display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:8px;background:var(--bg-light);'>
      <svg width='24' height='24' viewBox='0 0 24 24' fill='none'><path d='M8 17l-5-5 5-5M16 7l5 5-5 5' stroke='${getComputedStyle(document.documentElement).getPropertyValue('--primary').trim() || '#1976d2'}' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg>
      <span style='color:var(--primary);font-weight:500;'></span>
    </span>`;
    deployBtn.parentNode.appendChild(div);
    document.getElementById('code-svg-btn').onclick = async function() {
      const res = await fetch('/rules');
      const data = await res.json();
      showRulesModal(data);
    };
  }
}
insertCodeSvgButton();
// --- Initial render ---
render();
render();

function addThemeSelector() {
  ;
  
  // Appliquer le thème au chargement
  const saved = localStorage.getItem('theme') || 'system';
  select.value = saved;
  setTheme(saved);
}
function setTheme(theme) {
  if (theme === 'system') {
    // Détecte le thème système et applique light/dark
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.setAttribute('data-theme', 'light');
    }
  } else {
    document.documentElement.setAttribute('data-theme', theme);
  }
}

// Ajout et synchronisation du sélecteur de thème sur chaque section
function setupThemeSelectors() {
  document.querySelectorAll('.theme-selector').forEach(sel => {
    sel.innerHTML = `
      <option value="light">Clair</option>
      <option value="dark">Sombre</option>
      <option value="system">Système</option>
    `;
    sel.value = localStorage.getItem('theme') || 'system';
    sel.onchange = function() {
      setTheme(sel.value);
      localStorage.setItem('theme', sel.value);
      document.querySelectorAll('.theme-selector').forEach(s => s.value = sel.value);
    };
  });
}
window.addEventListener('DOMContentLoaded', setupThemeSelectors);

// Synchronisation du thème sur toutes les pages (hors SPA)
function syncThemeOnAllPages() {
  // Appliquer le thème au chargement
  const theme = localStorage.getItem('theme') || 'system';
  setTheme(theme);
  // Synchroniser tous les sélecteurs
  document.querySelectorAll('.theme-selector').forEach(sel => sel.value = theme);
  // Sur changement, stocker et recharger la page pour appliquer partout
  document.querySelectorAll('.theme-selector').forEach(sel => {
    sel.onchange = function() {
      localStorage.setItem('theme', sel.value);
      setTheme(sel.value);
      document.querySelectorAll('.theme-selector').forEach(s => s.value = sel.value);
      // Rechargement pour pages multi-vues
      if (window.location.pathname) {
        window.location.reload();
      }
    };
  });
}
window.addEventListener('DOMContentLoaded', syncThemeOnAllPages);

// --- Auth utilisateur local pour la section DB/Règles ---
let currentUser = null;

function renderAuthBox() {
  // Affiche le formulaire de connexion uniquement dans le simulateur de règles
  const simSection = document.getElementById('sim-collection')?.closest('div');
  if (!simSection) return;
  let authBox = document.getElementById('sim-auth-box');
  if (!authBox) {
    authBox = document.createElement('div');
    authBox.id = 'sim-auth-box';
    authBox.style.background = 'var(--bg-panel)';
    authBox.style.borderRadius = '10px';
    authBox.style.boxShadow = '0 2px 8px #0001';
    authBox.style.padding = '14px 18px';
    authBox.style.marginBottom = '12px';
    simSection.prepend(authBox);
  }
  if (!currentUser) {
    authBox.innerHTML = `
      <form id="sim-login-form" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        <input id="sim-login-email" type="text" placeholder="Email ou téléphone" style="padding:7px 12px;border-radius:6px;border:1px solid #1976d2;">
        <input id="sim-login-password" type="password" placeholder="Mot de passe" style="padding:7px 12px;border-radius:6px;border:1px solid #1976d2;">
        <button type="submit" style="background:#1976d2;color:#fff;padding:7px 18px;border-radius:6px;font-weight:bold;">Connexion</button>
        <span id="sim-login-msg" style="margin-left:10px;color:#c00;font-size:0.98em;"></span>
      </form>
    `;
    document.getElementById('sim-login-form').onsubmit = async function(e) {
      e.preventDefault();
      const email = document.getElementById('sim-login-email').value.trim();
      const password = document.getElementById('sim-login-password').value;
      const msg = document.getElementById('sim-login-msg');
      msg.textContent = '';
      try {
        const res = await fetch('/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: email, password })
        });
        if (!res.ok) {
          msg.textContent = (await res.json()).detail || 'Erreur de connexion';
          return;
        }
        const data = await res.json();
        currentUser = { email, token: data.access_token };
        localStorage.setItem('db_current_user', JSON.stringify(currentUser));
        renderAuthBox();
        showSnackbar('Connecté !', 'var(--color-success)');
      } catch (e) {
        msg.textContent = 'Erreur réseau';
      }
    };
  } else {
    authBox.innerHTML = `
      <span style='color:var(--color-success);font-weight:bold;'>Connecté en tant que ${currentUser.email}</span>
      <button id='sim-logout-btn' style='margin-left:18px;background:#e74c3c;color:#fff;padding:6px 16px;border-radius:6px;font-weight:bold;'>Déconnexion</button>
    `;
    document.getElementById('sim-logout-btn').onclick = function() {
      currentUser = null;
      localStorage.removeItem('db_current_user');
      renderAuthBox();
      showSnackbar('Déconnecté', 'var(--color-warning)');
    };
  }
}

window.addEventListener('DOMContentLoaded', function() {
  const saved = localStorage.getItem('db_current_user');
  if (saved) try { currentUser = JSON.parse(saved); } catch(e){}
  renderAuthBox();
});

// --- Affichage conditionnel du champ utilisateur dans le simulateur de règles ---
function updateSimAuthVisibility() {
  const col = document.getElementById("sim-collection")?.value;
  const act = document.getElementById("sim-action")?.value;
  const authDiv = document.getElementById("sim-auth-container");
  if (!col || !act || !authDiv) return;
  // Cherche la règle active
  const rule = rules.find(r => r.collection === col && r.action === act);
  // Affiche le champ uniquement si la condition contient "auth" ou "uid"
  if (rule && /auth(\.|\s|!=|==|\[|\]|\()/i.test(rule.condition)) {
    authDiv.style.display = '';
  } else {
    authDiv.style.display = 'none';
    document.getElementById("sim-auth").value = '';
  }
}

// --- Ajout listeners pour le simulateur ---
window.addEventListener('DOMContentLoaded', function() {
  const simCol = document.getElementById("sim-collection");
  const simAct = document.getElementById("sim-action");
  if(simCol) simCol.addEventListener('change', updateSimAuthVisibility);
  if(simAct) simAct.addEventListener('change', updateSimAuthVisibility);
  updateSimAuthVisibility();
});

// Sur modification des règles ou des collections, signaler le besoin de déployer
function markRulesDirty() {
  setDeployDirty(true);
}

// Hook sur les ajouts/suppressions de collection/doc/règle
const origAddCollection = addCollection;
addCollection = function() {
  origAddCollection.apply(this, arguments);
  markRulesDirty();
};
const origDeleteCollectionRecursively = deleteCollectionRecursively;
deleteCollectionRecursively = function() {
  origDeleteCollectionRecursively.apply(this, arguments);
  markRulesDirty();
};
const origAddRule = addRule;
addRule = function() {
  origAddRule.apply(this, arguments);
  markRulesDirty();
};
const origDeleteRule = deleteRule;
deleteRule = function() {
  origDeleteRule.apply(this, arguments);
  markRulesDirty();
};

function initThemeSelectors() {
  // Appliquer le thème au chargement
  const theme = localStorage.getItem('theme') || 'system';
  setTheme(theme);
  // Remplir tous les sélecteurs de thème
  document.querySelectorAll('.theme-selector').forEach(sel => {
    sel.innerHTML = `
      <option value="system">Système</option>
      <option value="light">Clair</option>
      <option value="dark">Sombre</option>`;
    sel.value = theme;
    sel.onchange = function() {
      localStorage.setItem('theme', sel.value);
      setTheme(sel.value);
      document.querySelectorAll('.theme-selector').forEach(s => s.value = sel.value);
    };
  });
}
window.initThemeSelectors = initThemeSelectors;