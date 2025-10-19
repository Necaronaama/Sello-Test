// Global variables
let brands = [];

// Initialize brand selection page
document.addEventListener('DOMContentLoaded', async function() {
    // Verificar autenticación
    const isAuthenticated = await checkAuth();
    if (!isAuthenticated) {
        return;
    }
    
    // Cargar marcas disponibles
    await loadBrands();
});

// Verificar autenticación
async function checkAuth() {
    try {
        const response = await fetch('/api/auth/profile', {
            credentials: 'include'
        });
        if (!response.ok) {
            // Si no está autenticado, redirigir al login
            window.location.href = 'index.html';
            return false;
        }
        
        const user = await response.json();
        
        // Si el usuario tiene rol 'public', redirigir directamente a su marca
        if (user.role === 'public' && user.brand_name) {
            sessionStorage.setItem('selectedBrand', user.brand_name);
            window.location.href = `index.html?brand=${encodeURIComponent(user.brand_name)}`;
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('Error al verificar autenticación:', error);
        window.location.href = 'index.html';
        return false;
    }
}

// Cargar marcas disponibles
async function loadBrands() {
    const loadingState = document.getElementById('loadingState');
    const brandsContainer = document.getElementById('brandsContainer');
    const noBrands = document.getElementById('noBrands');
    
    try {
        const response = await fetch("/api/brands", {
            credentials: 'include'
        });
        
        if (response.ok) {
            const brandsData = await response.json();
            brands = brandsData.sort();
            
            if (brands.length > 0) {
                renderBrands();
                loadingState.style.display = 'none';
                brandsContainer.style.display = 'grid';
            } else {
                loadingState.style.display = 'none';
                noBrands.style.display = 'block';
            }
        } else {
            throw new Error('Error al cargar dispositivos');
        }
    } catch (error) {
        console.error('Error loading brands:', error);
        loadingState.style.display = 'none';
        noBrands.style.display = 'block';
    }
}

// Renderizar marcas
async function renderBrands() {
    const brandsContainer = document.getElementById('brandsContainer');
    
    // Obtener información completa de cada marca incluyendo URL
    const brandPromises = brands.map(async brand => {
        try {
            const response = await fetch(`/api/brands/${encodeURIComponent(brand)}/info`, {
                credentials: 'include'
            });
            if (response.ok) {
                const brandInfo = await response.json();
                return { name: brand, url: brandInfo.url || null };
            }
        } catch (error) {
            console.error(`Error loading info for brand ${brand}:`, error);
        }
        return { name: brand, url: null };
    });
    
    const brandsWithInfo = await Promise.all(brandPromises);
    
    brandsContainer.innerHTML = brandsWithInfo.map(brandInfo => {
        const brand = brandInfo.name;
        const brandUrl = brandInfo.url;
        const qrUrl = `${window.location.origin}/index.html?brand=${encodeURIComponent(brand)}`;
        // Intentar múltiples formatos de imagen
        const brandImageUrl = getBrandImageUrl(brand);
        
        return `
            <div class="brand-card" onclick="selectBrand('${brand}')">
                <button class="edit-brand-btn" onclick="event.stopPropagation(); editBrand('${brand}')" title="Editar marca">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="delete-brand-btn" onclick="event.stopPropagation(); deleteBrand('${brand}')" title="Eliminar marca">
                    <i class="fas fa-trash"></i>
                </button>
                <button class="qr-brand-btn" onclick="event.stopPropagation(); showBrandQR('${brand}')" title="Código QR de la marca">
                    <i class="fas fa-qrcode"></i>
                </button>
                <div class="brand-name">${brand}</div>
                <div class="qr-container">
                    <div class="qr-code" id="qr-${brand.replace(/[^a-zA-Z0-9]/g, '')}"></div>
                </div>
                <div class="brand-image-container">
                    <img src="${brandImageUrl}" alt="" class="brand-image" 
                         onerror="handleImageError(this, '${brand}')">
                    <div class="brand-image-placeholder" style="display: none;">
                        Logo de ${brand}
                    </div>
                </div>
                ${brandUrl ? `
                    <a href="${brandUrl}" target="_blank" class="brand-url" onclick="event.stopPropagation();">
                        <i class="fas fa-external-link-alt"></i>
                        ${brandUrl}
                    </a>
                ` : ''}
                <div class="brand-info">
                    <i class="fas fa-qrcode"></i>
                    Escanea el código QR o haz clic para acceder
                </div>
                <button class="select-brand-btn" onclick="event.stopPropagation(); selectBrand('${brand}')">
                    <i class="fas fa-arrow-right"></i>
                    Acceder al Panel
                </button>
            </div>
        `;
    }).join('');
    
    // Generar códigos QR con tokens
    brands.forEach(async brand => {
        const qrElementId = `qr-${brand.replace(/[^a-zA-Z0-9]/g, '')}`;
        await generateQRWithToken(brand, qrElementId);
    });
}

// Función para obtener la URL de imagen de marca con múltiples formatos
function getBrandImageUrl(brandName) {
    const encodedBrand = encodeURIComponent(brandName);
    // Intentar primero JPG, luego JPEG, luego PNG
    return `static/uploads/brands/${encodedBrand}/${encodedBrand}.jpg`;
}

// Función para manejar errores de carga de imágenes
function handleImageError(imgElement, brandName) {
    const encodedBrand = encodeURIComponent(brandName);
    const currentSrc = imgElement.src;
    
    // Definir los formatos a intentar en orden
    const formats = ['jpg', 'jpeg', 'png'];
    const basePath = `static/uploads/brands/${encodedBrand}/${encodedBrand}`;
    
    // Determinar qué formato se está intentando actualmente
    let currentFormatIndex = -1;
    for (let i = 0; i < formats.length; i++) {
        if (currentSrc.includes(`.${formats[i]}`)) {
            currentFormatIndex = i;
            break;
        }
    }
    
    // Intentar el siguiente formato
    const nextFormatIndex = currentFormatIndex + 1;
    
    if (nextFormatIndex < formats.length) {
        // Intentar el siguiente formato
        const nextFormat = formats[nextFormatIndex];
        const nextUrl = `${basePath}.${nextFormat}`;
        imgElement.src = nextUrl;
    } else {
        // No hay más formatos que intentar, mostrar placeholder
        imgElement.style.display = 'none';
        
        // Mostrar el placeholder con el mensaje
        const placeholder = imgElement.nextElementSibling;
        if (placeholder && placeholder.classList.contains('brand-image-placeholder')) {
            placeholder.style.display = 'flex';
        }
    }
}

// Generar código QR con token
async function generateQRWithToken(brandName, elementId) {
    try {
        // Obtener QR con token del backend
        const response = await fetch(`/api/brands/${encodeURIComponent(brandName)}/qr-with-token`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            const qrElement = document.getElementById(elementId);
            if (qrElement) {
                // Crear imagen del QR
                const img = document.createElement('img');
                img.src = data.qr_code;
                img.alt = `QR Code for ${brandName}`;
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
                qrElement.innerHTML = '';
                qrElement.appendChild(img);
            }
        } else {
            // Fallback: generar QR sin token
            console.warn(`No se pudo generar QR con token para ${brandName}, usando método tradicional`);
            generateQRFallback(brandName, elementId);
        }
    } catch (error) {
        console.error('Error generating QR with token:', error);
        // Fallback: generar QR sin token
        generateQRFallback(brandName, elementId);
    }
}

// Función de respaldo para generar QR sin token
function generateQRFallback(brandName, elementId) {
    try {
        const qrUrl = `${window.location.origin}/index.html?brand=${encodeURIComponent(brandName)}`;
        const qr = qrcode(0, 'M');
        qr.addData(qrUrl);
        qr.make();
        
        const qrElement = document.getElementById(elementId);
        if (qrElement) {
            qrElement.innerHTML = qr.createImgTag(4, 8);
        }
    } catch (error) {
        console.error('Error generating fallback QR code:', error);
    }
}

// Seleccionar marca
function selectBrand(brand) {
    // Guardar marca seleccionada en sessionStorage
    sessionStorage.setItem('selectedBrand', brand);
    
    // Redirigir al panel con la marca seleccionada
    window.location.href = `index.html?brand=${encodeURIComponent(brand)}`;
}

// Función para cerrar sesión
async function logout() {
    try {
        await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
        
        // Redirigir al login
        window.location.href = 'index.html';
    } catch (error) {
        console.error('Error al cerrar sesión:', error);
        window.location.href = 'index.html';
    }
}

// Función para mostrar el QR de una marca
async function showBrandQR(brandName) {
    try {
        // Generar la URL de la marca
        const brandUrl = `${window.location.origin}/index.html?brand=${encodeURIComponent(brandName)}`;
        
        // Crear un contenedor temporal para generar el QR
        const tempDiv = document.createElement('div');
        tempDiv.style.display = 'none';
        document.body.appendChild(tempDiv);
        
        // Generar el código QR usando la librería qrcode-generator
        const qr = qrcode(0, 'M');
        qr.addData(brandUrl);
        qr.make();
        
        // Crear la imagen del QR
        const qrImageTag = qr.createImgTag(4, 8);
        tempDiv.innerHTML = qrImageTag;
        const qrImg = tempDiv.querySelector('img');
        const qrCodeDataUrl = qrImg.src;
        
        // Limpiar el contenedor temporal
        document.body.removeChild(tempDiv);
        
        // Crear modal para mostrar el QR
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="qr-modal-content">
                <div class="modal-header">
                    <h3>Código QR de la Marca</h3>
                    <button class="modal-close" onclick="closeBrandQRModal(this)">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="qr-container-modal">
                        <div class="brand-qr-info">
                            <h4>${brandName}</h4>
                        </div>
                        <div class="qr-code-container">
                            <img src="${qrCodeDataUrl}" alt="Código QR de la Marca" class="qr-code-image">
                        </div>
                        <div class="qr-url-info">
                            <p><strong>URL de la marca:</strong></p>
                            <div class="url-container">
                                <input type="text" value="${brandUrl}" readonly class="url-input" id="brandUrl${brandName.replace(/[^a-zA-Z0-9]/g, '')}">
                                <button class="btn btn-outline btn-sm" onclick="copyBrandUrlToClipboard('brandUrl${brandName.replace(/[^a-zA-Z0-9]/g, '')}')">
                                    <i class="fas fa-copy"></i> Copiar
                                </button>
                            </div>
                        </div>
                        <div class="qr-actions">
                            <button class="btn btn-primary" onclick="downloadBrandQR('${qrCodeDataUrl}', '${brandName}_QR')">
                                <i class="fas fa-download"></i> Descargar QR
                            </button>
                            <button class="btn btn-outline" onclick="window.open('${brandUrl}', '_blank')">
                                <i class="fas fa-external-link-alt"></i> Ver Panel
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Añadir estilos para el modal si no existen
        if (!document.getElementById('brandQRModalStyles')) {
            const styles = document.createElement('style');
            styles.id = 'brandQRModalStyles';
            styles.textContent = `
                .modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.5);
                    display: flex !important;
                    justify-content: center;
                    align-items: center;
                    z-index: 9999;
                }
                
                .qr-modal-content {
                    background: white;
                    border-radius: 15px;
                    padding: 0;
                    max-width: 500px;
                    width: 90%;
                    max-height: 90vh;
                    overflow-y: auto;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                    position: relative;
                    z-index: 10000;
                }
                
                .modal-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 15px 15px 0 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .modal-header h3 {
                    margin: 0;
                    font-size: 1.3rem;
                }
                
                .modal-close {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 1.5rem;
                    cursor: pointer;
                    padding: 0;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    transition: background-color 0.3s ease;
                }
                
                .modal-close:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
                
                .modal-body {
                    padding: 2rem;
                }
                
                .qr-container-modal {
                    text-align: center;
                }
                
                .brand-qr-info h4 {
                    color: #333;
                    margin-bottom: 1.5rem;
                    font-size: 1.4rem;
                    font-weight: 600;
                }
                
                .qr-code-container {
                    margin: 1.5rem 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                
                .qr-code-image {
                    max-width: 200px;
                    height: auto;
                    border: 2px solid #eee;
                    border-radius: 10px;
                    padding: 10px;
                    background: white;
                }
                
                .qr-url-info {
                    margin-top: 2rem;
                }
                
                .qr-url-info p {
                    margin-bottom: 0.5rem;
                    font-weight: 600;
                    color: #555;
                }
                
                .url-container {
                    display: flex;
                    align-items: center;
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 0.5rem;
                }
                
                .url-input {
                    flex-grow: 1;
                    border: none;
                    background: transparent;
                    font-size: 0.9rem;
                    color: #333;
                    padding: 0.3rem;
                    margin-right: 0.5rem;
                }
                
                .url-input:focus {
                    outline: none;
                }
                
                .qr-actions {
                    margin-top: 2rem;
                    display: flex;
                    justify-content: center;
                    gap: 1rem;
                }
                
                .btn {
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 0.8rem 1.5rem;
                    border-radius: 25px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    text-decoration: none;
                    border: 2px solid transparent;
                }
                
                .btn-primary {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                
                .btn-primary:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
                }
                
                .btn-outline {
                    background: transparent;
                    color: #667eea;
                    border-color: #667eea;
                }
                
                .btn-outline:hover {
                    background: #667eea;
                    color: white;
                    transform: translateY(-2px);
                }
                
                .btn-sm {
                    padding: 0.6rem 1rem;
                    font-size: 0.8rem;
                }
                
                @media (max-width: 768px) {
                    .qr-modal-content {
                        width: 95%;
                        margin: 1rem;
                        max-height: 85vh;
                    }
                    
                    .modal-body {
                        padding: 1.5rem;
                    }
                    
                    .qr-actions {
                        flex-direction: column;
                        gap: 0.8rem;
                    }
                    
                    .url-container {
                        flex-direction: column;
                        gap: 0.5rem;
                    }
                    
                    .url-input {
                        margin-bottom: 0;
                    }
                    
                    .btn {
                        justify-content: center;
                    }
                }
            `;
            document.head.appendChild(styles);
        }
        
        // Añadir el modal al DOM
        document.body.appendChild(modal);
        
        // Añadir event listener para cerrar al hacer clic fuera del modal
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeBrandQRModal(modal);
            }
        });
        
    } catch (error) {
        console.error('Error showing brand QR:', error);
        alert('Error al generar el código QR de la marca');
    }
}

// Función para cerrar el modal de QR de marca
function closeBrandQRModal(element) {
    // Buscar el modal padre
    let modal = element;
    while (modal && !modal.classList.contains('modal-overlay')) {
        modal = modal.parentElement;
    }
    
    if (modal) {
        document.body.removeChild(modal);
    }
}

// Función para copiar URL al portapapeles
function copyBrandUrlToClipboard(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.select();
        input.setSelectionRange(0, 99999); // Para móviles
        
        try {
            document.execCommand('copy');
            alert('URL copiada al portapapeles');
        } catch (err) {
            console.error('Error al copiar:', err);
            alert('Error al copiar la URL');
        }
    }
}

// Función para descargar el código QR
function downloadBrandQR(dataUrl, filename) {
    const link = document.createElement('a');
    link.download = filename + '.png';
    link.href = dataUrl;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    alert('Código QR descargado');
}

// Función para mostrar el modal de agregar marca
function showAddBrandModal() {
    const modal = document.getElementById('addBrandModal');
    modal.style.display = 'block';
}

// Función para cerrar el modal de agregar marca
function closeAddBrandModal() {
    const modal = document.getElementById('addBrandModal');
    modal.style.display = 'none';
    // Limpiar el formulario
    document.getElementById('addBrandForm').reset();
}

// Función para manejar el envío del formulario de nueva marca
document.addEventListener('DOMContentLoaded', function() {
    const addBrandForm = document.getElementById('addBrandForm');
    if (addBrandForm) {
        addBrandForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const newBrandName = document.getElementById('newBrandName').value.trim();
            const brandUser = document.getElementById('brandUser').value.trim();
            const brandPassword = document.getElementById('brandPassword').value.trim();
            
            if (!newBrandName) {
                alert('Por favor ingrese un nombre de marca válido');
                return;
            }
            
            if (!brandUser) {
                alert('Por favor ingrese un usuario de acceso');
                return;
            }
            
            if (!brandPassword) {
                alert('Por favor ingrese una contraseña de acceso');
                return;
            }
            
            // Verificar si la marca ya existe
            if (brands.includes(newBrandName)) {
                alert('Esta marca ya existe en el sistema');
                return;
            }
            
            try {
                // Crear FormData para manejar archivos
                const formData = new FormData();
                formData.append('marca', newBrandName);
                formData.append('user', brandUser);
                formData.append('password', brandPassword);
                
                const brandUrl = document.getElementById('brandUrl').value.trim();
                if (brandUrl) {
                    formData.append('url', brandUrl);
                }
                
                const imageFile = document.getElementById('brandImage').files[0];
                if (imageFile) {
                    formData.append('image', imageFile);
                }
                
                const response = await fetch('/api/brands', {
                    method: 'POST',
                    credentials: 'include',
                    body: formData
                });
                
                if (response.ok) {
                    // Cerrar modal
                    closeAddBrandModal();
                    
                    // Recargar las marcas
                    await loadBrands();
                    
                    alert('Marca agregada exitosamente');
                } else {
                    const error = await response.json();
                    alert('Error al agregar la marca: ' + (error.error || 'Error desconocido'));
                }
            } catch (error) {
                console.error('Error adding brand:', error);
                alert('Error de conexión al agregar la marca');
            }
        });
    }

    // Manejador del formulario de edición de marcas
    const editBrandForm = document.getElementById('editBrandForm');
    if (editBrandForm) {
        editBrandForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const newBrandName = document.getElementById('editBrandName').value.trim();
            const originalBrandName = document.getElementById('originalBrandName').value;
            
            if (!newBrandName) {
                alert('Por favor ingrese un nombre de marca válido');
                return;
            }
            
            // Verificar si el nuevo nombre ya existe (y no es el mismo nombre original)
            if (newBrandName !== originalBrandName && brands.includes(newBrandName)) {
                alert('Esta marca ya existe en el sistema');
                return;
            }
            
            try {
                // Crear FormData para manejar archivos
                const formData = new FormData();
                formData.append('newMarca', newBrandName);
                
                const brandUrl = document.getElementById('editBrandUrl').value.trim();
                if (brandUrl) {
                    formData.append('url', brandUrl);
                }
                
                const imageFile = document.getElementById('editBrandImage').files[0];
                if (imageFile) {
                    formData.append('image', imageFile);
                }
                
                const response = await fetch(`/api/brands/${encodeURIComponent(originalBrandName)}`, {
                    method: 'PUT',
                    credentials: 'include',
                    body: formData
                });
                
                if (response.ok) {
                    // Cerrar modal
                    closeEditBrandModal();
                    
                    // Recargar las marcas
                    await loadBrands();
                    
                    alert('Marca actualizada exitosamente');
                } else {
                    const error = await response.json();
                    alert('Error al actualizar la marca: ' + (error.error || 'Error desconocido'));
                }
            } catch (error) {
                console.error('Error updating brand:', error);
                alert('Error de conexión al actualizar la marca');
            }
        });
    }
});

// Cerrar modal al hacer clic fuera de él
window.addEventListener('click', function(event) {
    const addModal = document.getElementById('addBrandModal');
    const editModal = document.getElementById('editBrandModal');
    
    if (event.target === addModal) {
        closeAddBrandModal();
    }
    
    if (event.target === editModal) {
        closeEditBrandModal();
    }
});

// Función para eliminar marca
async function deleteBrand(brandName) {
    if (!confirm(`¿Estás seguro de que deseas eliminar la marca "${brandName}" y todos sus dispositivos? Esta acción no se puede deshacer.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/brands/${encodeURIComponent(brandName)}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (response.ok) {
            // Recargar las marcas
            await loadBrands();
            alert('Marca eliminada exitosamente');
            
            // Si no quedan marcas, forzar la recarga completa de la página para limpiar la visualización
            if (brands.length === 0) {
                window.location.reload();
            }
        } else {
            const error = await response.json();
            alert('Error al eliminar la marca: ' + (error.error || 'Error desconocido'));
        }
    } catch (error) {
        console.error('Error deleting brand:', error);
        alert('Error de conexión al eliminar la marca');
    }
}

// Función para mostrar el modal de editar marca
async function editBrand(brandName) {
    const modal = document.getElementById('editBrandModal');
    const editBrandNameInput = document.getElementById('editBrandName');
    const editBrandUrlInput = document.getElementById('editBrandUrl');
    const editBrandUserInput = document.getElementById('editbrandUser');
    const editBrandPasswordInput = document.getElementById('editbrandPassword');
    const originalBrandNameInput = document.getElementById('originalBrandName');
    
    editBrandNameInput.value = brandName;
    originalBrandNameInput.value = brandName;
    
    // Cargar la URL actual de la marca
    try {
        const response = await fetch(`/api/brands/${encodeURIComponent(brandName)}/info`, {
            credentials: 'include'
        });
        if (response.ok) {
            const brandInfo = await response.json();
            editBrandUrlInput.value = brandInfo.url || '';
        }
    } catch (error) {
        console.error(`Error loading brand info for ${brandName}:`, error);
        editBrandUrlInput.value = '';
    }

    // Cargar usuario y contraseña asociados a la marca
    try {
        const userResponse = await fetch(`/api/users/brand/${encodeURIComponent(brandName)}`, {
            credentials: 'include'
        });
        if (userResponse.ok) {
            const userData = await userResponse.json();
            editBrandUserInput.value = userData.email || '';
            editBrandPasswordInput.value = userData.password_hash || '';
        } else {
            editBrandUserInput.value = '';
            editBrandPasswordInput.value = '';
        }
    } catch (error) {
        console.error(`Error loading user credentials for brand ${brandName}:`, error);
        editBrandUserInput.value = '';
        editBrandPasswordInput.value = '';
    }
    
    modal.style.display = 'block';
}

// Función para cerrar el modal de editar marca
function closeEditBrandModal() {
    const modal = document.getElementById('editBrandModal');
    modal.style.display = 'none';
    // Limpiar el formulario
    document.getElementById('editBrandForm').reset();
}

// Función para alternar la visibilidad de la contraseña
function togglePasswordVisibility(inputId) {
    const passwordInput = document.getElementById(inputId);
    const toggleIcon = passwordInput.nextElementSibling.querySelector("i");
    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        toggleIcon.classList.remove("fa-eye");
        toggleIcon.classList.add("fa-eye-slash");
    } else {
        passwordInput.type = "password";
        toggleIcon.classList.remove("fa-eye-slash");
        toggleIcon.classList.add("fa-eye");
    }
}

