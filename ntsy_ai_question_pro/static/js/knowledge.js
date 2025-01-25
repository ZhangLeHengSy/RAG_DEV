// static/js/knowledge.js
document.addEventListener('DOMContentLoaded', function () {
    const createForm = document.getElementById('createKnowledgeBaseForm');
    const uploadForm = document.getElementById('uploadForm');
    const knowledgeBaseSelect = document.getElementById('knowledgeBaseSelect');

    // 加载知识库列表
    async function loadKnowledgeBases() {
        try {
            const response = await axios.get('/api/knowledge/list');
            const bases = response.data;
            knowledgeBaseSelect.innerHTML = '<option value="">请选择知识库...</option>';
            bases.forEach(base => {
                const option = document.createElement('option');
                option.value = base.name;
                option.textContent = base.name;
                knowledgeBaseSelect.appendChild(option);
            });
        } catch (error) {
            console.error('加载知识库失败:', error);
            alert('加载知识库失败');
        }
    }

    // 创建知识库
    createForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const name = document.getElementById('knowledgeBaseName').value;

        try {
            await axios.post('/api/knowledge/create', { name });
            alert('知识库创建成功');
            loadKnowledgeBases();
            createForm.reset();
        } catch (error) {
            console.error('创建知识库失败:', error);
            alert('创建知识库失败');
        }
    });

    // 上传文件
    uploadForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const files = document.getElementById('files').files;
        const knowledgeBase = knowledgeBaseSelect.value;

        if (!knowledgeBase) {
            alert('请选择知识库');
            return;
        }

        const formData = new FormData();
        formData.append('knowledge_base', knowledgeBase);
        Array.from(files).forEach(file => {
            formData.append('files[]', file);
        });

        const progressBar = document.querySelector('#uploadProgress');
        progressBar.classList.remove('d-none');

        try {
            await axios.post('/api/knowledge/upload', formData, {
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    progressBar.querySelector('.progress-bar').style.width = percentCompleted + '%';
                }
            });

            alert('文件上传成功');
            uploadForm.reset();
            progressBar.classList.add('d-none');
        } catch (error) {
            console.error('上传文件失败:', error);
            alert('上传文件失败');
            progressBar.classList.add('d-none');
        }
    });

    // 删除知识库
    async function deleteKnowledgeBase(name) {
        if (!confirm(`确定要删除知识库 "${name}" 吗？这个操作不可撤销。`)) {
            return;
        }

        try {
            await axios.post('/api/knowledge/delete', { name });
            alert('知识库删除成功');
            loadKnowledgeBases();
        } catch (error) {
            console.error('删除知识库失败:', error);
            alert('删除知识库失败: ' + (error.response?.data?.error || error.message));
        }
    }

    // 获取知识库信息
    async function getKnowledgeBaseInfo(name) {
        try {
            const response = await axios.get(`/api/knowledge/${name}/info`);
            const info = response.data;

            // 更新UI显示知识库信息
            const infoDiv = document.getElementById('knowledgeBaseInfo');
            if (infoDiv) {
                infoDiv.innerHTML = `
                <div class="card-body">
                    <h5 class="card-title">${info.name}</h5>
                    <p class="card-text">文档数量: ${info.document_count}</p>
                    <p class="card-text">创建时间: ${new Date(info.created_at * 1000).toLocaleString()}</p>
                    <button class="btn btn-danger btn-sm" onclick="deleteKnowledgeBase('${info.name}')">
                        删除知识库
                    </button>
                </div>
            `;
            }
        } catch (error) {
            console.error('获取知识库信息失败:', error);
        }
    }

    // 在知识库选择变化时更新信息
    knowledgeBaseSelect.addEventListener('change', function () {
        const selectedBase = this.value;
        if (selectedBase) {
            getKnowledgeBaseInfo(selectedBase);
        }
    });

    // 初始加载知识库列表
    loadKnowledgeBases();
});