fetch('/api/ladder-global', {
    method: 'GET',
    credentials: 'same-origin'
})
.then((response)=>{
    return response.json();
})
.then((body)=>{
    console.log(body)
});
