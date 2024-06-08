let balance = 0;
let count = document.getElementById("count");

let tg = window.Telegram.WebApp;
tg.expand();

let user;

let is_playing = false;


let rangs_names = [
    "wood",
    "bronze",
    "silver",
    "gold",
    "platina",
    "diamond",
    "kryptonite"
]

let rangs = {
    "wood": "assets/wood.png",
    "bronze": "assets/bronze.png",
    "silver": "assets/silver.png",
    "gold": "assets/gold.png",
    "platina": "assets/platina.png",
    "diamond": "assets/diamond.png",
    "kryptonite": "assets/kryptonite.png",
};


let rangs_from = {
    "wood": 0,
    "bronze": 10000,
    "silver": 100000,
    "gold": 500000,
    "platina": 1000000,
    "diamond": 10000000,
    "kryptonite": 50000000,
}


function closehandler(object){
    if (!this.isExpanded){
        this.expand()
    }
}

tg.onEvent('viewportChanged', closehandler);


let cbtn = document.getElementById("canstart");
let ctst = document.getElementById("cantstart");

let intrv_to_star;
let seconds_to_ses;

let free_try = 3;


function random_start_speed() {
    let speed_abs = 0.5;
    let speed_vrs = [speed_abs, -speed_abs];
    return speed_vrs[Math.floor(Math.random()*speed_vrs.length)];
}


function toHHMMSS(secs) {
    var sec_num = parseInt(secs, 10)
    var hours   = Math.floor(sec_num / 3600)
    var minutes = Math.floor(sec_num / 60) % 60
    var seconds = sec_num % 60

    return [hours,minutes,seconds]
        .map(v => v < 10 ? "0" + v : v)
        .filter((v,i) => v !== "00" || i > 0)
        .join(":")
}


function intr_w() {
    if (seconds_to_ses <= 0) {
        cbtn.hidden = false;
        ctst.hidden = true;

        clearInterval(intrv_to_star);
    } else {
        seconds_to_ses--;
        ctst.innerText = toHHMMSS(seconds_to_ses);
    }

}

function wait_session() {
    fetch("/api/time_to_session", {
        method: "POST",
        headers: {
            accept: "application/json",
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ tg_id: tg.initDataUnsafe.user.id }),
    })
    .then((res) => {
        return res.json();
    })
    .then((data) => {
        let tts = data.tts;

        if (tts == 0) {
            cbtn.hidden = false;
        } else {
            seconds_to_ses = tts;
            ctst.hidden = false;

            intrv_to_star = setInterval(intr_w, 1000);
        }
    });
}


const queryString = window.location.search;
console.log(queryString, "!!!!!");
const urlParams = new URLSearchParams(queryString);

const invite = urlParams.get('invite');

let shlink = document.getElementById("shlink"); 

let reqqq;

console.log(invite);

reqqq = { tg_id: tg.initDataUnsafe.user.id, nick: tg.initDataUnsafe.user.username, friend_id: invite };

if (! reqqq.nick) {
    reqqq.nick = tg.initDataUnsafe.user.first_name;
}

frindslist = document.getElementById("frindslist");

fetch("/api/connect", {
        method: "POST",
        headers: {
            accept: "application/json",
            "Content-Type": "application/json",
        },
        body: JSON.stringify(reqqq),
    })
    .then((res) => {
        return res.json();
    })
    .then((data) => {
        balance = data.balance;
        add_to_balance(0);
        user = data;
        shlink.innerText = "https://t.me/voboru_bot?start=" + user.id;

        wait_session(data.can_next_session_after);
    });

function add_to_balance(add_cnt) {
    balance += add_cnt;
    count.innerText = balance;
}

let main_block = document.getElementById("main");
let clicker_block = document.getElementById("clicker");
let menu_block = document.getElementById("start_menu");
let canvas = document.getElementById("game_canvas");
let ctx = canvas.getContext("2d");

canvas.width = canvas.offsetWidth;
canvas.height = canvas.offsetHeight;

// function on_resize() {
//     canvas.width = canvas.offsetWidth;
//     canvas.height = canvas.offsetHeight;
// }

// window.onresize = on_resize;

var ballRadius = 105;
var clicked_delta = 2;

let is_clicked = false;
let clicked_time = 10;
let clicked_time_spend = clicked_time;

var x = canvas.width;
// var y = canvas.height - ballRadius;
var y = canvas.height / 2;

var dx = random_start_speed();
var dy = random_start_speed();

let spead_mode = 4;

let add_cnt = 1;

let miss_clicks = 0;
// let misscl = document.getElementById("misscl");

let hearts = document.getElementById("hearts");

let heart_1 = document.getElementById("heart-1");
let heart_2 = document.getElementById("heart-2");
let heart_3 = document.getElementById("heart-3");

let timeprogress = document.getElementById("timeprogress");

function set_time_progress(time, all_time) {
    // let p = Math.round(time / all_time * 100);
    let p = time / all_time * 100;
    timeprogress.style.width = `${p}%`;
}


function show_heats(cnth) {
    if (cnth >= 3) {
        heart_1.src = "assets/heart.png";
        heart_2.src = "assets/heart.png";
        heart_3.src = "assets/heart.png";
    }
    if (cnth == 2) {
        heart_1.src = "assets/heart.png";
        heart_2.src = "assets/heart.png";
        heart_3.src = "assets/heart_miss.png";
    }
    if (cnth == 1) {
        heart_1.src = "assets/heart.png";
        heart_2.src = "assets/heart_miss.png";
        heart_3.src = "assets/heart_miss.png";
    }
    if (cnth <= 0) {
        heart_1.src = "assets/heart_miss.png";
        heart_2.src = "assets/heart_miss.png";
        heart_3.src = "assets/heart_miss.png";
    }
}

function hide_hearts(is_hide) {
    if (is_hide) {
        heart_1.hidden = true;
        heart_2.hidden = true;
        heart_3.hidden = true;
    } else {
        heart_1.hidden = false;
        heart_2.hidden = false;
        heart_3.hidden = false;
    }
}

show_heats(3);
hide_hearts(true);

var coin_img = document.getElementById("coin_img");

function show_cnt_up(cnt, x, y) {
    let d = document.createElement("div");
    d.className = "cntup";
    d.innerHTML = `+${cnt}`;
    d.style.left = `${x}px`;
    d.style.top = `${y}px`;
    document.body.append(d);


    setTimeout(function() {
        d.classList.add("hid");
        d.style.top = `${y - 100}px`;
        setTimeout(function() {
            d.remove();
        }, 800);
    }, 100);
}


canvas.addEventListener("click", function(event) {
    let rect = canvas.getBoundingClientRect();
    let clickX = event.clientX - rect.left;
    let clickY = event.clientY - rect.top;

    if (
        x - ballRadius <= clickX &&
        clickX <= x + ballRadius &&
        y - ballRadius <= clickY &&
        clickY <= y + ballRadius
    ) {
        // console.log("Клик внутри круга!");
        add_to_balance(add_cnt);
        is_clicked = true;
        show_cnt_up(add_cnt, event.clientX, event.clientY - 80);
    } else {
        miss_clicks++;
        show_heats(3 - miss_clicks);

        if (miss_clicks >= 3) {
            end_session("miss");
        }
    }
    console.log(clickX, clickY, x, y);
});

function draw_coin() {
    ctx.beginPath();
    // ctx.arc(x, y, ballRadius, 0, Math.PI * 2);
    // ctx.fillStyle = "blue";
    // ctx.fill();
    if (is_clicked) {
        if (clicked_time_spend > 0) {
            ctx.drawImage(
                coin_img,
                x - ballRadius + clicked_delta,
                y - ballRadius + clicked_delta,
                (ballRadius - clicked_delta) * 2,
                (ballRadius - clicked_delta) * 2
            );
            clicked_time_spend--;
        } else {
            ctx.drawImage(
                coin_img,
                x - ballRadius,
                y - ballRadius,
                ballRadius * 2,
                ballRadius * 2
            );
            clicked_time_spend = clicked_time;
            is_clicked = false;
        }
    } else {
        ctx.drawImage(
            coin_img,
            x - ballRadius,
            y - ballRadius,
            ballRadius * 2,
            ballRadius * 2
        );
    }

    ctx.closePath();
}

function add_speed() {
    let rnd = Math.random() * 0.0005;

    if (dx >= 0) dx += rnd;
    else dx -= rnd;

    if (dy >= 0) dy += rnd;
    else dy -= rnd;
}




function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    draw_coin();

    if (user.session_time * check_per - session_time > 30) {
        if (x + dx > canvas.width - ballRadius || x + dx < ballRadius) {
            add_speed();
            dx = -dx;
        }
        if (y + dy > canvas.height - ballRadius || y + dy < ballRadius) {
            add_speed();
            dy = -dy;
        }

        x += dx;
        y += dy;
    }


}

function secondsToMinutesSeconds(seconds) {
    var minutes = Math.floor(seconds / 60);
    var remainingSeconds = seconds % 60;
    var formattedSeconds =
        remainingSeconds < 10 ? "0" + remainingSeconds : remainingSeconds;
    return minutes + ":" + formattedSeconds;
}

// clicker_block.style.display = "none";
let session_time = 0;
let session_interval;
let draw_interwal;


clicker_block.style.display = "none";
menu_block.style.display = "block";

function end_session(res) {
    clicker_block.style.display = "none";
    menu_block.style.display = "block";

    is_playing = false;

    miss_clicks = 0;
    show_heats(3 - miss_clicks);
    hide_hearts(true);

    session_time = 0;
    clearInterval(session_interval);
    clearInterval(draw_interwal);

    cbtn.hidden = true;
    ctst.hidden = true;

    fetch("/api/save_session", {
        method: "POST",
        headers: {
            accept: "application/json",
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            tg_id: tg.initDataUnsafe.user.id,
            balance: balance,
        }),
    })
    .then((res) => {
        return res.json();
    })
    .then((data) => {
        user = data;
        wait_session(data.can_next_session_after);
    });

    miss_clicks = 0;

    ballRadius = 105;
    clicked_delta = 10;

    is_clicked = false;
    clicked_time = 10;
    clicked_time_spend = clicked_time;

    x = canvas.width / 2;
    // y = canvas.height - ballRadius;
    y = canvas.height / 2;


    dx = random_start_speed();
    dy = random_start_speed();
    if (res == "time") {
        tg.showPopup({message: "Время вышло!", buttons: [{id: "ok", type: "ok", text: "OK"}]});
    }
    if (res == "miss") {
        tg.showPopup({message: "Вы промахнолусь 3 раза!", buttons: [{id: "ok", type: "ok", text: "OK"}]});
    }
}

let check_per = 200;


function chacnge_speed(d) {
    if (dx >= 0) dx += d;
    else dx -= d;

    if (dy >= 0) dy += d;
    else dy -= d;

    console.log("change", dx, dy);
}



function session_check() {
    set_time_progress(session_time, user.session_time * check_per);
    session_time--;

    if (session_time <= 0) {
        end_session("time");
    }
    let p = session_time / (user.session_time * check_per) * 100;
    // if (p % 5 == 0) console.log(p);
    p -= 5;

    if (spead_mode == 4 && p <= 75) {
        spead_mode = 3;
        add_cnt = 2;
        chacnge_speed(0.7);
    }
    if (spead_mode == 3 && 25 <= p && p < 50) {
        spead_mode = 2;
        add_cnt = 3;
        chacnge_speed(0.7);
    }
    if (spead_mode == 2 && p <= 25) {
        spead_mode = 1;
        add_cnt = 4;
        chacnge_speed(0.7);
    }


}

function start_session() {
    is_playing = true;
    set_time_progress(user.session_time, user.session_time);
    spead_mode = 4;
    add_cnt = 1;
    draw_interwal = setInterval(draw, 10);
    clicker_block.style.display = "block";
    menu_block.style.display = "none";
    miss_clicks = 0;
    show_heats(3 - miss_clicks);
    hide_hearts(false);
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    session_time = user.session_time * check_per;
    session_interval = setInterval(session_check, 5);
}


cbtn.onclick = start_session;

// start_session();

// setInterval(draw, 10);


let show_rang_id;

function get_persent(a, b) {
    let res = (a / b) * 100;
    res = res.toFixed(2);

    if (res > 100) {
        res = 100;
    }

    return res;
}


function show_rang(rang_id) {

    // document.getElementById("rang_prev").hidden = false;
    // document.getElementById("rang_next").hidden = false;
    // if (rang_id == 0) {
    //     document.getElementById("rang_prev").hidden = true;
    // }
    // if (rang_id == rangs_names.length - 1) {
    //     document.getElementById("rang_next").hidden = true;
    // }

    // document.getElementById("rang_title").innerText = rangs_names[rang_id].toUpperCase();
    // document.getElementById("rang_img").src = rangs[rangs_names[rang_id]];
    // document.getElementById("rang_from").innerText = `From ${rangs_from[rangs_names[rang_id]]}`;
    // document.getElementById("rangprogress").style.width = `${get_persent(user.balance, rangs_from[rangs_names[rang_id]])}%`;
}


function prev_rang() {
    show_rang_id -= 1;
    show_rang(show_rang_id);
}

function next_rang() {
    show_rang_id += 1;
    show_rang(show_rang_id);
}

// document.getElementById("rang_prev").onclick = prev_rang;
// document.getElementById("rang_next").onclick = next_rang;



function show_tasks() {
    // let tasks_block = document.getElementById("tasksblock");
    // tasks_block.innerHTML = "";
    // for (let i = 0; i < user.tasks.length; i++) {
    //     let t = user.tasks[i];
    //     let ppt = get_persent(user.balance, rangs_from[t.info]);

    //     let is_active_task = "";
    //     if (user.balance >= rangs_from[t.info]) {
    //         is_active_task = "task_claim_active";
    //     }

    //     tasks_block.innerHTML += `<div class="task" id="task_${t.info}">
    //                                 <img src="${rangs[t.info]}" class="task_img">
    //                                 <div class="task_info">
    //                                     <div class="task_title">${t.title}</div>
    //                                     <div class="task_cnt">
    //                                         <img src="assets/coin_mini.png">
    //                                         <div id="task_cnt">${t.cnt}</div>
    //                                     </div>
    //                                     <div class="taskprogblock">
    //                                         <div class="taskline">
    //                                             <span style="width: ${ppt}%"></span>
    //                                         </div>
    //                                     </div>
    //                                 </div>
    //                                 <div class="task_claim ${is_active_task}" onclick="claim_task('${t.info}')">Claim</div>
    //                             </div>`
    // }
}


function claim_task(task_inf) {
    // fetch("/api/claim_task", {
    //     method: "POST",
    //     headers: {
    //         accept: "application/json",
    //         "Content-Type": "application/json",
    //     },
    //     body: JSON.stringify({
    //         tg_id: tg.initDataUnsafe.user.id,
    //         task_info: task_inf,
    //     }),
    // })
    // .then((res) => {
    //     return res.json();
    // })
    // .then((data) => {
    //     balance = data.balance;
    //     add_to_balance(0);
    //     user = data;

    //     show_rang_id = rangs_names.indexOf(user.rang);
        
    //     show_rang(show_rang_id);
    //     show_tasks();
    // });
}



function hide_all() {
    // clicker_block.style.display = "none";
    // menu_block.style.display = "none";
    // frindsblock.style.display = "none";
    // earnblock.style.display = "none";

    // is_friends_open = false;
    // is_earnblock_open = false;
    // document.querySelectorAll(".bbb").forEach((el) => {
    //     el.classList.remove("bbb_active");
    // });
}


function open_friends(event) {
    // if (is_friends_open) {
    //     hide_all();

    //     if (is_playing) {
    //         clicker_block.style.display = "block";
    //     } else {
    //         menu_block.style.display = "block";
    //     }

    // } else {
    //     hide_all();
    //     frindsblock.style.display = "block";
    //     is_friends_open = true;
    //     document.getElementById("frinds_btn").classList.add("bbb_active");


    //     fetch("/api/get_friends", {
    //         method: "POST",
    //         headers: {
    //             accept: "application/json",
    //             "Content-Type": "application/json",
    //         },
    //         body: JSON.stringify({ tg_id: tg.initDataUnsafe.user.id }),
    //     })
    //     .then((res) => {
    //         return res.json();
    //     })
    //     .then((data) => {
    //         let friends = data.friends;
    //         frindslist.innerHTML = "";
    //         for (let i = 0; i < friends.length; i++) {
    //             console.log(friends[i]);

    //             frindslist.innerHTML += `<div class="friend">
    //                                         <img class="friend_rang" src="${rangs[friends[i].rang]}">
    //                                         <div class="friend_name">${friends[i].nick}</div>
    //                                         <div class="friend_balance">
    //                                             <img src="assets/coin_mini.png" class="friend_cnt_img">
    //                                             <div class="friend_cnt">${friends[i].for_invite}</div>
    //                                         </div>
    //                                     </div>`;
    //         }
    //     });

    // }
}

function open_earnblock(event) {
    // if (is_earnblock_open) {
    //     hide_all();

    //     if (is_playing) {
    //         clicker_block.style.display = "block";
    //     } else {
    //         menu_block.style.display = "block";
    //     }

    // } else {
    //     hide_all();
    //     earnblock.style.display = "block";
    //     is_earnblock_open = true;
    //     document.getElementById("earn_btn").classList.add("bbb_active");

    //     show_rang_id = rangs_names.indexOf(user.rang);
        
    //     show_rang(show_rang_id);
    //     show_tasks();

    // }
}



// document.getElementById("frinds_btn").onclick = open_friends;
// document.getElementById("earn_btn").onclick = open_earnblock;


document.getElementById("divers").offsetWidth = document.getElementById("timerline").offsetWidth;


// shlink.onclick = navigator.clipboard.writeText(shlink.innerText)