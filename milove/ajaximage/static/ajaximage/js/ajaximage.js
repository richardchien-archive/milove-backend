(function () {
    "use strict";

    var getCookie = function (name) {
        var value = '; ' + document.cookie,
            parts = value.split('; ' + name + '=');
        if (parts.length === 2) return parts.pop().split(';').shift()
    };

    var request = function (method, url, data, headers, el, showProgress, cb) {
        var req = new XMLHttpRequest();
        req.open(method, url, true);

        Object.keys(headers).forEach(function (key) {
            req.setRequestHeader(key, headers[key]);
        });

        req.onload = function () {
            cb(req.status, req.responseText);
        };

        req.onerror = function () {
            error(el, 'Failed to upload image.');
        };

        req.upload.onprogress = function (data) {
            progressBar(el, data, showProgress);
        };

        req.send(data);

        return req;
    };

    var parseJson = function (json) {
        var data;
        try {
            data = JSON.parse(json);
        } catch (e) {
            data = null;
        }
        return data;
    };

    var getEl = function (childEl) {
        var el = childEl.parentElement;
        while (el && !el.classList.contains('ajaximage')) {
            el = el.parentElement;
        }
        if (!el) {
            el = null;
        }
        return el;
    };

    var progressBar = function (el, data, showProgress) {
        if (data.lengthComputable === false || showProgress === false) return;

        var pcnt = Math.round(data.loaded * 100 / data.total),
            bar = el.querySelector('.bar');

        bar.style.width = pcnt + '%';
    };

    var error = function (el, msg) {
        el.querySelector('.ajaximage-file-input').value = '';
        el.querySelector('.ajaximage-img').src = '';
        el.className = 'ajaximage ajaximage-idle';
        el.querySelector('.bar').style.width = '0%';
        disableSubmit(false);
        alert(msg);
    };

    var update = function (el, data) {
        var pathInput = el.querySelector('.ajaximage-path-input'),
            path = el.querySelector('.ajaximage-path');

        pathInput.value = data.path;
        path.innerText = data.path;

        el.className = 'ajaximage ajaximage-idle';
        el.querySelector('.bar').style.width = '0%';
    };

    var concurrentUploads = 0;
    var disableSubmit = function (status) {
        var submitRow = document.querySelector('.submit-row');
        if (!submitRow) return;

        var buttons = submitRow.querySelectorAll('input[type=submit]');

        if (status === true) concurrentUploads++;
        else concurrentUploads--;

        [].forEach.call(buttons, function (el) {
            el.disabled = (concurrentUploads !== 0);
        });
    };

    var upload = function (e) {
        var el = getEl(e.target),
            url = el.querySelector('.ajaximage-upload-url').value,
            file = el.querySelector('.ajaximage-file-input').files[0],
            img = el.querySelector('.ajaximage-img'),
            form = new FormData(),
            headers = {'X-CSRFToken': getCookie('csrftoken')},
            regex = /jpg|jpeg|png|gif/i;

        if (!regex.test(file.type)) {
            return alert('Incorrect image format. Allowed (jpg, gif, png).');
        }

        el.className = 'ajaximage ajaximage-uploading';
        disableSubmit(true);
        form.append('file', file);

        var fr = new FileReader();
        fr.onload = function () {
            img.src = fr.result;
        };
        fr.readAsDataURL(file);

        el.uploadRequest = request('POST', url, form, headers, el, true, function (status, json) {
            disableSubmit(false);

            var data = parseJson(json);

            switch (status) {
                case 200:
                    update(el, data);
                    break;
                case 400:
                case 403:
                case 404:
                    error(el, data.error);
                    break;
                default:
                    error(el, 'Sorry, could not upload image.');
                    break;
            }
        });
    };

    var cancelUpload = function (e) {
        e.preventDefault();

        disableSubmit(false);
        var el = getEl(e.target);
        if (el.uploadRequest) {
            el.uploadRequest.abort();
            el.uploadRequest = undefined;
        }
        el.querySelector('.ajaximage-file-input').value = '';
        el.querySelector('.ajaximage-img').src = '';
        el.className = 'ajaximage ajaximage-idle';
        el.querySelector('.bar').style.width = '0%';
    };

    var addHandlers = function (el) {
        var input = el.querySelector('.ajaximage-file-input'),
            cancel = el.querySelector('.ajaximage-cancel');

        el.className = 'ajaximage ajaximage-idle';

        cancel.addEventListener('click', cancelUpload, false);
        input.addEventListener('change', upload, false);
    };

    document.addEventListener('DOMContentLoaded', function (e) {
        [].forEach.call(document.querySelectorAll('.ajaximage'), addHandlers);
    });

    document.addEventListener('DOMNodeInserted', function (e) {
        if (e.target.tagName) {
            var el = e.target.querySelector('.ajaximage');
            if (el) addHandlers(el);
        }
    });
})();