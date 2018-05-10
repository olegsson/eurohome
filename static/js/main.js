function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const session_data = {
    logged_in: logged_in,
    own_votes: own_votes,
    ladder: [],
    users: [],
    viewing_user: null,
    voting_for: null,
    votes_allowed: [...Array(10).keys()].map(i => i+1),
    search_str: ''
};

const app = new Vue({
    el: '#app',
    data: session_data,
    methods: {
        vote: (country, magnitude) => fetch(
            `/api/vote?country=${encodeURIComponent(country)}`
            +`&magnitude=${magnitude}`, {
                credentials: 'same-origin'
            }
        ).then(resolve => {
            session_data.own_votes[session_data.voting_for] = magnitude;
            update_ladder();
        }),
        set_country: country => {
            session_data.viewing_user = null;
            session_data.voting_for = country;
            session_data.search_str = '';
            update_ladder();
        },
        set_user: user => {
            session_data.voting_for = null;
            session_data.viewing_user = user;
            session_data.search_str = '';
            update_ladder();
        },
        update: () => update_ladder(),
        filtered_ladder: () => {
            if (session_data.search_str === '') {
                return session_data.ladder;
            }
            return fuzzysort.go(
                session_data.search_str, session_data.ladder, {
                    key: 'country'
                }
            ).map(x => x.obj);
        }
    }
});

function resp_handler(resolve) {
    if (!resolve.ok) {
        session_data.logged_in = false;
        throw Error(resolve.statusText);
    }
    return resolve.json();
}

async function update_ladder(step=null) {
    let url;
    let user = session_data.viewing_user;
    if (session_data.logged_in && user !== null) {
        url = '/api/ladder-user?name=' + user;
    } else {
        url = '/api/public/ladder-global';
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
    if (step !== null) {
        await sleep(step);
        update_ladder(step);
    }
}

async function update_users(step=null) {
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
        if (step !== null) {
            await sleep(step);
            update_users(step);
        }
    } else {
        session_data.users = [];
    }
}

update_ladder(1000);
update_users(1000);
