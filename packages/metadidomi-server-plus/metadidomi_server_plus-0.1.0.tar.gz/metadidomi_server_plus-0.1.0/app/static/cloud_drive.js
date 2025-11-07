
    // Configuration
    const BACKEND_URL = 'http://127.0.0.1:5003';
    const USERS_KEY = 'cloud_users';
    const CURRENT_USER_KEY = 'current_cloud_user';
    const SESSION_EXPIRY_KEY = 'cloud_session_expiry';
    const FILES_KEY = 'cloud_files';
    const FOLDERS_KEY = 'cloud_folders';
    const NAVIGATION_KEY = 'cloud_navigation';
    const SESSION_DURATION = 60 * 60 * 1000; // 1 heure
    const MAX_STORAGE = 15 * 1024 * 1024 * 1024; // 15 Go

    // Éléments DOM
    const authSection = document.getElementById('auth-section');
    const mainSection = document.getElementById('main-section');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const loginAlert = document.getElementById('login-alert');
    const registerAlert = document.getElementById('register-alert');
    const userGreeting = document.getElementById('user-greeting');
    const filesList = document.getElementById('files_list');
    const themeSelector = document.getElementById('theme-selector');
    const breadcrumb = document.getElementById('breadcrumb');
    const backendStatus = document.getElementById('backend-status');
    const previewModal = document.getElementById('preview-modal');
    const previewTitle = document.getElementById('preview-title');
    const previewBody = document.getElementById('preview-body');
    const snackbar = document.getElementById('snackbar');
    const snackbarMessage = document.getElementById('snackbar-message');
    const snackbarIcon = document.getElementById('snackbar-icon');

    // État de navigation
    let currentFolderId = '';
    let navigationHistory = [];
    let currentHistoryIndex = -1;
    let isBackendOnline = false;

    // Initialisation
    document.addEventListener('DOMContentLoaded', function() {
      checkAuthStatus();
      setupEventListeners();
      initThemeSelector();
      loadNavigationState();
      
      // Tester la connexion au backend
      testBackendConnection();
    });

    // Vérifier le statut d'authentification
    function checkAuthStatus() {
      const currentUser = getCurrentUser();
      const sessionExpiry = localStorage.getItem(SESSION_EXPIRY_KEY);
      
      if (sessionExpiry && Date.now() > parseInt(sessionExpiry)) {
        logout();
        showSnackbar('Session expirée. Veuillez vous reconnecter.', 'error');
        return;
      }
      
      if (currentUser) {
        showMainSection(currentUser);
      } else {
        showAuthSection();
      }
    }

    // Afficher la section d'authentification
    function showAuthSection() {
      authSection.classList.remove('hidden');
      mainSection.classList.add('hidden');
      showLoginForm();
    }

    // Afficher la section principale
    function showMainSection(user) {
      authSection.classList.add('hidden');
      mainSection.classList.remove('hidden');
      
      userGreeting.textContent = `Bonjour, ${user.name}`;
      loadFilesList();
      loadAccountInfo();
      updateBreadcrumb();
    }

    // Afficher le formulaire de connexion
    function showLoginForm() {
      loginForm.classList.remove('hidden');
      registerForm.classList.add('hidden');
      clearAlerts();
    }

    // Afficher le formulaire d'inscription
    function showRegisterForm() {
      loginForm.classList.add('hidden');
      registerForm.classList.remove('hidden');
      clearAlerts();
    }

    // Configurer les écouteurs d'événements
    function setupEventListeners() {
      document.getElementById('loginForm').addEventListener('submit', handleLogin);
      document.getElementById('registerForm').addEventListener('submit', handleRegister);
      
      document.getElementById('show-register').addEventListener('click', function(e) {
        e.preventDefault();
        showRegisterForm();
      });
      
      document.getElementById('show-login').addEventListener('click', function(e) {
        e.preventDefault();
        showLoginForm();
      });

      themeSelector.addEventListener('change', function() {
        setTheme(this.value);
      });
    }

    // Initialiser le sélecteur de thème
    function initThemeSelector() {
      const savedTheme = localStorage.getItem('cloud_theme') || 'light';
      themeSelector.value = savedTheme;
      setTheme(savedTheme);
    }

    // Définir le thème
    function setTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('cloud_theme', theme);
    }

    // Tester la connexion au backend
    function testBackendConnection() {
      fetch(`${BACKEND_URL}/api/health`)
        .then(response => response.json())
        .then(data => {
          isBackendOnline = true;
          backendStatus.innerHTML = '<span class="status-indicator status-online"></span><span>Backend connecté</span>';
          console.log('✅ Backend connecté');
        })
        .catch(error => {
          isBackendOnline = false;
          backendStatus.innerHTML = '<span class="status-indicator status-offline"></span><span>Backend hors ligne</span>';
          console.log('❌ Backend hors ligne');
        });
    }

    // Mettre à jour le statut du backend
    function updateBackendStatus(online) {
      isBackendOnline = online;
      if (online) {
        backendStatus.innerHTML = '<span class="status-indicator status-online"></span><span>Backend connecté</span>';
      } else {
        backendStatus.innerHTML = '<span class="status-indicator status-offline"></span><span>Backend hors ligne</span>';
      }
    }

    // Tester le backend
    function testBackend() {
      showSnackbar('Test de connexion au backend...', 'info');
      
      fetch(`${BACKEND_URL}/api/health`)
        .then(response => response.json())
        .then(data => {
          updateBackendStatus(true);
          showSnackbar('✅ Backend connecté et opérationnel!', 'success');
        })
        .catch(error => {
          updateBackendStatus(false);
          showSnackbar('❌ Backend injoignable. Vérifiez que python backend.py est lancé.', 'error');
        });
    }

    // Charger depuis le cloud avec confirmation
    function loadFromCloud() {
      if (!confirm('Charger les données du cloud va écraser vos données locales. Continuer ?')) {
        showSnackbar('Chargement annulé', 'info');
        return;
      }
      console.log('🔄 Chargement des données depuis le cloud...');
      fetch(`${BACKEND_URL}/api/get_data`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Erreur HTTP ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('📥 Données reçues du backend:', data);
        if (data.success) {
          // Convertir les données du backend vers le format frontend
          const backendUsers = data.users || [];
          const backendFolders = data.folders || [];
          const backendFiles = data.files || [];
          // Mapper les utilisateurs
          const users = backendUsers.map(u => ({
            id: u.id,
            name: u.name,
            email: u.email,
            password: u.password,
            storageUsed: u.storage_used || 0,
            maxStorage: u.max_storage || MAX_STORAGE
          }));
          // Mapper les dossiers
          const folders = backendFolders.map(f => ({
            id: f.id,
            userId: f.user_id,
            name: f.name,
            parentId: f.parent_id,
            created: new Date(f.created_at).getTime() || Date.now()
          }));
          // Mapper les fichiers (sans contenu pour l'instant)
          const files = backendFiles.map(f => ({
            id: f.id,
            userId: f.user_id,
            folderId: f.folder_id,
            name: f.name,
            size: f.size,
            type: f.type,
            content: '', // Contenu vide pour l'instant
            modified: new Date(f.modified_at).getTime() || Date.now()
          }));
          // Sauvegarder dans le localStorage
          saveUsers(users);
          saveFolders(folders);
          saveFiles(files);
          // Mettre à jour l'interface
          updateBackendStatus(true);
          loadFilesList();
          loadAccountInfo();
          showSnackbar('✅ Données chargées depuis le cloud SQLite', 'success');
        } else {
          showSnackbar('❌ Erreur backend: ' + data.error, 'error');
        }
      })
      .catch(error => {
        console.error('❌ Erreur de chargement:', error);
        updateBackendStatus(false);
        showSnackbar('❌ Impossible de charger depuis le backend', 'error');
      });
    }

    // Charger l'état de navigation
    function loadNavigationState() {
      const navState = localStorage.getItem(NAVIGATION_KEY);
      if (navState) {
        const state = JSON.parse(navState);
        navigationHistory = state.history || [];
        currentHistoryIndex = state.index || -1;
        currentFolderId = state.currentFolderId || '';
      }
    }

    // Sauvegarder l'état de navigation
    function saveNavigationState() {
      const state = {
        history: navigationHistory,
        index: currentHistoryIndex,
        currentFolderId: currentFolderId
      };
      localStorage.setItem(NAVIGATION_KEY, JSON.stringify(state));
    }

    // Naviguer vers un dossier
    function navigateToFolder(folderId) {
      if (currentHistoryIndex < navigationHistory.length - 1) {
        navigationHistory = navigationHistory.slice(0, currentHistoryIndex + 1);
      }
      navigationHistory.push({ folderId: currentFolderId });
      currentHistoryIndex = navigationHistory.length - 1;
      
      currentFolderId = folderId;
      loadFilesList();
      updateBreadcrumb();
      saveNavigationState();
      
      const folder = getFolderById(folderId);
      const folderName = folder ? folder.name : 'Racine';
      showSnackbar(`Ouverture du dossier "${folderName}"`, 'info');
    }

    // Mettre à jour le fil d'Ariane
    function updateBreadcrumb() {
      let html = '<a onclick="navigateToFolder(\'\')">gs://mon-cloud</a>';
      
      if (currentFolderId) {
        const folder = getFolderById(currentFolderId);
        if (folder) {
          let path = [];
          let current = folder;
          while (current) {
            path.unshift(current);
            current = current.parentId ? getFolderById(current.parentId) : null;
          }
          
          for (const f of path) {
            html += ` / <a onclick="navigateToFolder('${f.id}')">${f.name}</a>`;
          }
        }
      }
      
      breadcrumb.innerHTML = html;
    }

    // Gérer la connexion
    function handleLogin(e) {
      e.preventDefault();
      clearAlerts();
      
      const email = document.getElementById('login-email').value;
      const password = document.getElementById('login-password').value;
      
      const users = getUsers();
      const user = users.find(u => u.email === email && u.password === password);
      
      if (user) {
        setCurrentUser(user);
        setSessionExpiry();
        showMainSection(user);
        showSnackbar('Connexion réussie!', 'success');
        // Charger depuis le cloud
        loadFromCloud();
      } else {
        showAlert(loginAlert, 'Email ou mot de passe incorrect.');
      }
    }

    // Gérer l'inscription
    function handleRegister(e) {
      e.preventDefault();
      clearAlerts();
      
      const name = document.getElementById('register-name').value;
      const email = document.getElementById('register-email').value;
      const password = document.getElementById('register-password').value;
      const confirmPassword = document.getElementById('register-confirm-password').value;
      
      if (password !== confirmPassword) {
        showAlert(registerAlert, 'Les mots de passe ne correspondent pas.');
        return;
      }
      
      const users = getUsers();
      
      if (users.find(u => u.email === email)) {
        showAlert(registerAlert, 'Un compte avec cet email existe déjà.');
        return;
      }
      
      const newUser = {
        id: generateId(),
        name: name,
        email: email,
        password: password,
        storageUsed: 0,
        maxStorage: MAX_STORAGE
      };
      
      users.push(newUser);
      saveUsers(users);
      
      setCurrentUser(newUser);
      setSessionExpiry();
      showMainSection(newUser);
      
      showSnackbar('Compte créé avec succès!', 'success');
      // Charger depuis le cloud
      loadFromCloud();
    }

    // Déconnexion
    function logout() {
      localStorage.removeItem(CURRENT_USER_KEY);
      localStorage.removeItem(SESSION_EXPIRY_KEY);
      showAuthSection();
      showSnackbar('Déconnexion réussie', 'info');
    }

    // Sauvegarder vers le cloud
    function saveToCloud() {
      console.log('💾 Début de la sauvegarde vers le cloud...');
      
      const currentUser = getCurrentUser();
      if (!currentUser) {
        showSnackbar('Vous devez être connecté pour sauvegarder', 'error');
        return;
      }

      // Récupérer toutes les données actuelles
      const users = getUsers();
      const files = getFiles();
      const folders = getFolders();
      
      console.log('📊 Données à sauvegarder:', {
        users: users.length,
        folders: folders.length,
        files: files.length
      });

      // Préparer les données pour l'envoi
      const payload = {
        users: users,
        files: files.map(file => ({
          ...file,
          // S'assurer que le contenu est en base64
          content: file.content && file.content.startsWith('data:') 
                  ? file.content.split(',')[1] 
                  : file.content
        })),
        folders: folders
      };

      // Envoyer au backend
      fetch(`${BACKEND_URL}/api/cloud_sync`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          action: 'push_all',
          ...payload
        })
      })
      .then(async response => {
        console.log('📨 Réponse HTTP:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Erreur ${response.status}: ${errorText}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('✅ Réponse du backend:', data);
        
        if (data.success) {
          updateBackendStatus(true);
          showSnackbar('✅ Données sauvegardées avec succès dans SQLite!', 'success');
          
          // Recharger les données depuis le backend pour vérification
          setTimeout(() => loadFromCloud(), 1000);
        } else {
          showSnackbar('❌ Erreur de sauvegarde: ' + (data.error || 'Inconnue'), 'error');
        }
      })
      .catch(error => {
        console.error('❌ Erreur de sauvegarde:', error);
        updateBackendStatus(false);
        showSnackbar('❌ Impossible de se connecter au backend. Démarrer: python backend.py', 'error');
      });
    }

    // Charger depuis le cloud
    function loadFromCloud() {
      console.log('🔄 Chargement des données depuis le cloud...');
      
      fetch(`${BACKEND_URL}/api/get_data`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Erreur HTTP ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('📥 Données reçues du backend:', data);
        
        if (data.success) {
          // Convertir les données du backend vers le format frontend
          const backendUsers = data.users || [];
          const backendFolders = data.folders || [];
          const backendFiles = data.files || [];
          
          // Mapper les utilisateurs
          const users = backendUsers.map(u => ({
            id: u.id,
            name: u.name,
            email: u.email,
            password: u.password,
            storageUsed: u.storage_used || 0,
            maxStorage: u.max_storage || MAX_STORAGE
          }));
          
          // Mapper les dossiers
          const folders = backendFolders.map(f => ({
            id: f.id,
            userId: f.user_id,
            name: f.name,
            parentId: f.parent_id,
            created: new Date(f.created_at).getTime() || Date.now()
          }));
          
          // Mapper les fichiers (sans contenu pour l'instant)
          const files = backendFiles.map(f => ({
            id: f.id,
            userId: f.user_id,
            folderId: f.folder_id,
            name: f.name,
            size: f.size,
            type: f.type,
            content: '', // Contenu vide pour l'instant
            modified: new Date(f.modified_at).getTime() || Date.now()
          }));
          
          // Sauvegarder dans le localStorage
          saveUsers(users);
          saveFolders(folders);
          saveFiles(files);
          
          // Mettre à jour l'interface
          updateBackendStatus(true);
          loadFilesList();
          loadAccountInfo();
          showSnackbar('✅ Données chargées depuis le cloud SQLite', 'success');
        } else {
          showSnackbar('❌ Erreur backend: ' + data.error, 'error');
        }
      })
      .catch(error => {
        console.error('❌ Erreur de chargement:', error);
        updateBackendStatus(false);
        showSnackbar('❌ Impossible de charger depuis le backend', 'error');
      });
    }

    // Charger la liste des fichiers et dossiers
    function loadFilesList() {
      const currentUser = getCurrentUser();
      const files = getFiles().filter(f => f.userId === currentUser.id && f.folderId === currentFolderId);
      const folders = getFolders().filter(f => f.userId === currentUser.id && f.parentId === currentFolderId);
      
      filesList.innerHTML = '';
      
      if (folders.length === 0 && files.length === 0) {
        filesList.innerHTML = '<tr><td colspan="6" class="empty-state">Ce dossier est vide</td></tr>';
        return;
      }
      
      // Afficher d'abord les dossiers
      folders.forEach(folder => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
          <td><input type="checkbox" class="item-checkbox" data-id="${folder.id}" data-type="folder"></td>
          <td><span class="folder-icon">📁</span> ${folder.name}</td>
          <td>-</td>
          <td>Dossier</td>
          <td>${new Date(folder.created).toLocaleString()}</td>
          <td class="actions">
            <button class="btn-primary" onclick="navigateToFolder('${folder.id}')">
              <svg class="svg-icon" viewBox="0 0 24 24" width="16" height="16">
                <path d="M5,17L9.5,12L5,7V17H13V15H7V13H13V11H7V9H13V7H15V17H5Z"/>
              </svg>
            </button>
            <button class="btn-icon tooltip" onclick="renameFolder('${folder.id}')">
              <svg class="svg-icon" viewBox="0 0 24 24" width="16" height="16">
                <path d="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z"/>
              </svg>
              <span class="tooltiptext">Renommer</span>
            </button>
            <button class="btn-danger tooltip" onclick="deleteFolder('${folder.id}')">
              <svg class="svg-icon" viewBox="0 0 24 24" width="16" height="16">
                <path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"/>
              </svg>
              <span class="tooltiptext">Supprimer</span>
            </button>
          </td>
        `;
        
        filesList.appendChild(row);
      });
      
      // Puis les fichiers
      files.forEach(file => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
          <td><input type="checkbox" class="item-checkbox" data-id="${file.id}" data-type="file"></td>
          <td><span class="file-icon">📄</span> ${file.name}</td>
          <td>${formatFileSize(file.size)}</td>
          <td>${file.type}</td>
          <td>${new Date(file.modified).toLocaleString()}</td>
          <td class="actions">
            <button class="btn-primary tooltip" onclick="previewFile('${file.id}')">
              <svg class="svg-icon" viewBox="0 0 24 24" width="16" height="16">
                <path d="M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z"/>
              </svg>
              <span class="tooltiptext">Prévisualiser</span>
            </button>
            <button class="btn-primary tooltip" onclick="downloadFile('${file.id}')">
              <svg class="svg-icon" viewBox="0 0 24 24" width="16" height="16">
                <path d="M5,20H19V18H5M19,9H15V3H9V9H5L12,16L19,9Z"/>
              </svg>
              <span class="tooltiptext">Télécharger</span>
            </button>
            <button class="btn-primary tooltip" onclick="copyDownloadLink('${file.id}')">
              <svg class="svg-icon" viewBox="0 0 24 24" width="16" height="16">
                <path d="M19,21H8V7H19M19,5H8A2,2 0 0,0 6,7V21A2,2 0 0,0 8,23H19A2,2 0 0,0 21,21V7A2,2 0 0,0 19,5M16,1H4A2,2 0 0,0 2,3V17H4V3H16V1Z"/>
              </svg>
              <span class="tooltiptext">Copier le lien</span>
            </button>
            <button class="btn-icon tooltip" onclick="renameFile('${file.id}')">
              <svg class="svg-icon" viewBox="0 0 24 24" width="16" height="16">
                <path d="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z"/>
              </svg>
              <span class="tooltiptext">Renommer</span>
            </button>
            <button class="btn-danger tooltip" onclick="deleteFile('${file.id}')">
              <svg class="svg-icon" viewBox="0 0 24 24" width="16" height="16">
                <path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"/>
              </svg>
              <span class="tooltiptext">Supprimer</span>
            </button>
          </td>
        `;
        
        filesList.appendChild(row);
      });
    }

    // Charger les informations du compte
    function loadAccountInfo() {
      const currentUser = getCurrentUser();
      const files = getFiles().filter(f => f.userId === currentUser.id);
      const storageUsed = files.reduce((total, file) => total + file.size, 0);
      const usagePercent = Math.min((storageUsed / currentUser.maxStorage) * 100, 100);
      
      document.getElementById('account_info').innerHTML = `
        <h3>Informations du compte</h3>
        <p><strong>Nom:</strong> ${currentUser.name}</p>
        <p><strong>Email:</strong> ${currentUser.email}</p>
        <div class="storage-info">
          <span><strong>Espace utilisé:</strong> ${formatFileSize(storageUsed)} / ${formatFileSize(currentUser.maxStorage)}</span>
          <div class="storage-bar">
            <div class="storage-fill" style="width: ${usagePercent}%"></div>
          </div>
        </div>
        <p><strong>Dossiers:</strong> ${getFolders().filter(f => f.userId === currentUser.id).length}</p>
        <p><strong>Fichiers:</strong> ${files.length}</p>
        <p><strong>Backend:</strong> ${isBackendOnline ? '✅ Connecté' : '❌ Hors ligne'}</p>
      `;
    }

    // Créer un dossier
    function createFolder() {
      const folderName = prompt('Nom du dossier:');
      if (!folderName) return;
      
      const currentUser = getCurrentUser();
      const folders = getFolders();
      
      const existingFolder = folders.find(f => 
        f.userId === currentUser.id && 
        f.parentId === currentFolderId && 
        f.name === folderName
      );
      
      if (existingFolder) {
        showSnackbar('Un dossier avec ce nom existe déjà', 'error');
        return;
      }
      
      const newFolder = {
        id: generateId(),
        userId: currentUser.id,
        name: folderName,
        parentId: currentFolderId,
        created: Date.now()
      };
      
      folders.push(newFolder);
      saveFolders(folders);
      loadFilesList();
      showSnackbar(`Dossier "${folderName}" créé avec succès`, 'success');
      
      // Synchroniser avec le backend
      if (isBackendOnline) {
        fetch(`${BACKEND_URL}/api/cloud_sync`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'create_folder', folder: newFolder })
        });
      }
    }

    // Renommer un dossier
    function renameFolder(folderId) {
      const folder = getFolderById(folderId);
      if (!folder) return;
      
      const newName = prompt('Nouveau nom du dossier:', folder.name);
      if (!newName || newName === folder.name) return;
      
      const folders = getFolders();
      const folderIndex = folders.findIndex(f => f.id === folderId);
      
      if (folderIndex !== -1) {
        const oldName = folders[folderIndex].name;
        folders[folderIndex].name = newName;
        saveFolders(folders);
        loadFilesList();
        showSnackbar('Dossier renommé avec succès', 'success');
        
        // Synchroniser avec le backend
        if (isBackendOnline) {
          fetch(`${BACKEND_URL}/api/cloud_sync`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'rename_folder', folderId, newName })
          });
        }
      }
    }

    // Supprimer un dossier
    function deleteFolder(folderId) {
      if (!confirm('Êtes-vous sûr de vouloir supprimer ce dossier? Tous les fichiers et sous-dossiers seront également supprimés.')) {
        return;
      }
      
      const folder = getFolderById(folderId);
      if (!folder) return;
      
      function deleteFolderRecursive(id) {
        const subFolders = getFolders().filter(f => f.parentId === id);
        const files = getFiles().filter(f => f.folderId === id);
        
        let allFiles = getFiles();
        allFiles = allFiles.filter(f => f.folderId !== id);
        saveFiles(allFiles);
        
        for (const subFolder of subFolders) {
          deleteFolderRecursive(subFolder.id);
        }
        
        let allFolders = getFolders();
        allFolders = allFolders.filter(f => f.id !== id);
        saveFolders(allFolders);
      }
      
      deleteFolderRecursive(folderId);
      loadFilesList();
      loadAccountInfo();
      showSnackbar('Dossier supprimé avec succès', 'success');
      
      // Synchroniser avec le backend
      if (isBackendOnline) {
        fetch(`${BACKEND_URL}/api/cloud_sync`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'delete_folder', folderId })
        });
      }
    }

    // Prévisualiser un fichier
    function previewFile(fileId) {
      const files = getFiles();
      const file = files.find(f => f.id === fileId);
      
      if (!file) return;
      
      previewTitle.textContent = `Prévisualisation: ${file.name}`;
      previewBody.innerHTML = '';
      
      if (file.type.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(new Blob([file.content], { type: file.type }));
        img.className = 'image-preview';
        img.onload = () => URL.revokeObjectURL(img.src);
        previewBody.appendChild(img);
      } else if (file.type === 'text/plain' || file.type.startsWith('text/')) {
        const pre = document.createElement('pre');
        pre.className = 'file-preview';
        pre.textContent = file.content.substring(0, 10000);
        previewBody.appendChild(pre);
      } else {
        previewBody.innerHTML = `<p>Prévisualisation non disponible pour ce type de fichier (${file.type}).</p>`;
      }
      
      previewModal.style.display = 'block';
    }

    // Fermer la prévisualisation
    function closePreview() {
      previewModal.style.display = 'none';
    }

    // Copier le lien de téléchargement
    function copyDownloadLink(fileId) {
      const file = getFiles().find(f => f.id === fileId);
      if (!file) return;
      
      const downloadUrl = URL.createObjectURL(new Blob([file.content], { type: file.type }));
      
      navigator.clipboard.writeText(downloadUrl).then(() => {
        showSnackbar('Lien de téléchargement copié dans le presse-papiers', 'success');
        setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);
      }).catch(err => {
        showSnackbar('Erreur lors de la copie du lien', 'error');
      });
    }

    // Télécharger un fichier
    function downloadFile(fileId) {
      const files = getFiles();
      const file = files.find(f => f.id === fileId);
      
      if (file) {
        const blob = new Blob([file.content], { type: file.type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.name;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showSnackbar(`Téléchargement de ${file.name} commencé`, 'success');
      }
    }

    // Renommer un fichier
    function renameFile(fileId) {
      const files = getFiles();
      const file = files.find(f => f.id === fileId);
      if (!file) return;
      
      const newName = prompt('Nouveau nom du fichier:', file.name);
      if (!newName || newName === file.name) return;
      
      const fileIndex = files.findIndex(f => f.id === fileId);
      if (fileIndex !== -1) {
        const oldName = files[fileIndex].name;
        files[fileIndex].name = newName;
        saveFiles(files);
        loadFilesList();
        showSnackbar('Fichier renommé avec succès', 'success');
        
        // Synchroniser avec le backend
        if (isBackendOnline) {
          fetch(`${BACKEND_URL}/api/cloud_sync`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'rename_file', fileId, newName })
          });
        }
      }
    }

    // Supprimer un fichier
    function deleteFile(fileId) {
      if (confirm('Êtes-vous sûr de vouloir supprimer ce fichier?')) {
        const files = getFiles();
        const file = files.find(f => f.id === fileId);
        const updatedFiles = files.filter(f => f.id !== fileId);
        saveFiles(updatedFiles);
        loadFilesList();
        loadAccountInfo();
        showSnackbar('Fichier supprimé avec succès', 'success');
        
        // Synchroniser avec le backend
        if (isBackendOnline) {
          fetch(`${BACKEND_URL}/api/cloud_sync`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'delete_file', fileId })
          });
        }
      }
    }

    // Importer un fichier
    function uploadFile() {
      const fileInput = document.getElementById('file_input');
      const files = fileInput.files;
      
      if (!files || files.length === 0) return;
      
      const currentUser = getCurrentUser();
      let allFiles = getFiles();
      const storageUsed = allFiles.filter(f => f.userId === currentUser.id)
                              .reduce((total, f) => total + f.size, 0);
      
      let totalNewSize = 0;
      for (let i = 0; i < files.length; i++) {
        totalNewSize += files[i].size;
      }
      
      if (storageUsed + totalNewSize > currentUser.maxStorage) {
        showSnackbar('Espace de stockage insuffisant', 'error');
        return;
      }
      
      let uploadedCount = 0;
      
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        const existingFile = allFiles.find(f => 
          f.userId === currentUser.id && 
          f.folderId === currentFolderId && 
          f.name === file.name
        );
        
        if (existingFile) {
          if (!confirm(`Le fichier "${file.name}" existe déjà. Voulez-vous le remplacer?`)) {
            continue;
          }
          allFiles = allFiles.filter(f => f.id !== existingFile.id);
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
          const newFile = {
            id: generateId(),
            userId: currentUser.id,
            folderId: currentFolderId,
            name: file.name,
            size: file.size,
            type: file.type || 'Inconnu',
            modified: Date.now(),
            content: e.target.result
          };
          
          allFiles.push(newFile);
          saveFiles(allFiles);
          
          // Synchroniser avec le backend
          if (isBackendOnline) {
            fetch(`${BACKEND_URL}/api/cloud_sync`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ action: 'upload_file', file: newFile })
            });
          }
          
          uploadedCount++;
          if (uploadedCount === files.length) {
            loadFilesList();
            loadAccountInfo();
            showSnackbar(`${uploadedCount} fichier(s) importé(s) avec succès`, 'success');
          }
        };
        reader.readAsDataURL(file);
      }
      
      fileInput.value = '';
    }

    // Sélectionner/désélectionner tous les éléments
    function toggleSelectAll(checkbox) {
      const itemCheckboxes = document.querySelectorAll('.item-checkbox');
      itemCheckboxes.forEach(cb => {
        cb.checked = checkbox.checked;
      });
    }

    // Supprimer le compte
    function deleteAccount() {
      if (confirm('Êtes-vous sûr de vouloir supprimer votre compte? Toutes vos données seront perdues.')) {
        const currentUser = getCurrentUser();
        const users = getUsers().filter(u => u.id !== currentUser.id);
        const files = getFiles().filter(f => f.userId !== currentUser.id);
        const folders = getFolders().filter(f => f.userId !== currentUser.id);
        
        saveUsers(users);
        saveFiles(files);
        saveFolders(folders);
        logout();
        showSnackbar('Compte supprimé avec succès', 'success');
      }
    }

    // Afficher le snackbar
    function showSnackbar(message, type = 'success') {
      const icons = {
        success: '<svg class="svg-icon" viewBox="0 0 24 24" width="20" height="20"><path d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"/></svg>',
        error: '<svg class="svg-icon" viewBox="0 0 24 24" width="20" height="20"><path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/></svg>',
        info: '<svg class="svg-icon" viewBox="0 0 24 24" width="20" height="20"><path d="M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/></svg>'
      };
      
      snackbarIcon.innerHTML = icons[type] || icons.info;
      snackbarMessage.textContent = message;
      
      snackbar.className = 'show';
      snackbar.classList.add(type);
      
      clearTimeout(snackbar.timeout);
      snackbar.timeout = setTimeout(() => {
        snackbar.className = snackbar.className.replace('show', '');
      }, 5000);
    }

    // Cacher le snackbar
    function hideSnackbar() {
      snackbar.className = snackbar.className.replace('show', '');
    }

    // Obtenir un dossier par son ID
    function getFolderById(folderId) {
      return getFolders().find(f => f.id === folderId);
    }

    // Fonctions utilitaires pour le localStorage
    function getUsers() {
      const usersJSON = localStorage.getItem(USERS_KEY);
      return usersJSON ? JSON.parse(usersJSON) : [];
    }

    function saveUsers(users) {
      localStorage.setItem(USERS_KEY, JSON.stringify(users));
    }

    function getCurrentUser() {
      const userJSON = localStorage.getItem(CURRENT_USER_KEY);
      return userJSON ? JSON.parse(userJSON) : null;
    }

    function setCurrentUser(user) {
      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
    }

    function setSessionExpiry() {
      const expiryTime = Date.now() + SESSION_DURATION;
      localStorage.setItem(SESSION_EXPIRY_KEY, expiryTime.toString());
    }

    function getFiles() {
      try {
        const filesJSON = localStorage.getItem(FILES_KEY);
        return filesJSON ? JSON.parse(filesJSON) : [];
      } catch (e) {
        return [];
      }
    }

    function saveFiles(files) {
      localStorage.setItem(FILES_KEY, JSON.stringify(files));
    }

    function getFolders() {
      try {
        const foldersJSON = localStorage.getItem(FOLDERS_KEY);
        return foldersJSON ? JSON.parse(foldersJSON) : [];
      } catch (e) {
        return [];
      }
    }

    function saveFolders(folders) {
      localStorage.setItem(FOLDERS_KEY, JSON.stringify(folders));
    }

    function generateId() {
      return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    function formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function showAlert(alertElement, message) {
      alertElement.textContent = message;
      alertElement.classList.remove('hidden');
    }

    function clearAlerts() {
      loginAlert.classList.add('hidden');
      registerAlert.classList.add('hidden');
    }

    // Fermer la modal en cliquant à l'extérieur
    window.onclick = function(event) {
      if (event.target === previewModal) {
        closePreview();
      }
    }
