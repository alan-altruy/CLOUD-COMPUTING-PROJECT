document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('login-form');
    const alertBox = document.getElementById('login-alert');
    const loginButton = document.getElementById('login-button');
    const togglePassword = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password');

    function showAlert(message) {
        alertBox.textContent = message;
        alertBox.classList.remove('d-none');
    }

    function hideAlert() {
        alertBox.classList.add('d-none');
        alertBox.textContent = '';
    }

    togglePassword && togglePassword.addEventListener('click', function () {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            togglePassword.textContent = 'Hide';
        } else {
            passwordInput.type = 'password';
            togglePassword.textContent = 'Show';
        }
    });

    form && form.addEventListener('submit', function (e) {
        e.preventDefault();
        hideAlert();

        const formData = new FormData(form);
        const email = formData.get('email') || '';
        const password = formData.get('password') || '';

        if (!email.trim() || !password.trim()) {
            showAlert('Please fill in the email and password.');
            return;
        }

        loginButton.disabled = true;
        loginButton.textContent = 'Logging in...';

        fetch(form.action || '/login', {
            method: form.method || 'post',
            body: formData,
        }).then(async (resp) => {
            loginButton.disabled = false;
            loginButton.textContent = 'Sign In';

            if (resp.redirected) {
                window.location = resp.url;
                return;
            }

            const contentType = resp.headers.get('content-type') || '';
            if (resp.ok) {
                // si API renvoie JSON
                if (contentType.includes('application/json')) {
                    const data = await resp.json();
                    if (data.success) {
                        window.location = data.next || '/';
                        return;
                    }
                    showAlert(data.message || 'Login failed');
                    return;
                }

                // fallback: reload page
                window.location.reload();
                return;
            }

            // erreur
            let text = await resp.text();
            try { text = JSON.parse(text).message || text; } catch (e) {}
            showAlert(text || 'Error occurred while logging in');
        }).catch((err) => {
            loginButton.disabled = false;
            loginButton.textContent = 'Sign In';
            showAlert('Unable to contact the server. Please try again later.');
            console.error(err);
        });
    });
});
