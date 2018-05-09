function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const session_data = {
    logged_in: logged_in,
    ladder: [],
    users: [],
    viewing_user: null
};

const app = new Vue({
    el: '#app',
    data: session_data,
    methods: {
        logout: () => {
            session_data.logged_in = false;
        }
    }
});

function resp_handler (resolve) {
    if (!resolve.ok) {
        session_data.logged_in = false;
        throw Error(resolve.statusText);
    }
    return resolve.json()
}

async function update_ladder() {
    let url;
    let user = session_data.viewing_user;
    if (session_data.logged_in && user !== null) {
        url = '/api/ladder-user?name=' + user
        credentials = 'same-origin'
    } else {
        url = '/api/public/ladder-global'
        credentials = 'same-origin'
    }
    await fetch(url, {
        method: 'GET',
        credentials: 'same-origin'
    })
    .then(resp_handler)
    .then(data => {
        session_data.ladder = data;
    })
    .catch(reject => {});
    await sleep(1000);
    update_ladder();
}

async function update_users() {
    if (session_data.logged_in) {
        await fetch('/api/users', {
            method: 'GET',
            credentials: 'same-origin'
        })
        .then(resp_handler)
        .then(data => {
            session_data.users = data;
        })
        .catch(reject => {});
        await sleep(1000);
        update_users();
    } else {
        session_data.users = [];
    }
}

update_ladder()
update_users()
