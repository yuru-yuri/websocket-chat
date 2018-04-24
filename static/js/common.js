
;((d, w) => {
    'use strict';

    function post(url, data) {
        data = data || {};
        return fetch(url, {
            credentials: 'include',
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    d.addEventListener('DOMContentLoaded', () => {
        const _https = w.location.protocol === 'https:';
        const url = (_https ? 'wss://' : 'ws://') + w.location.host + '/ws/';
        const RPC = WSRPC(url, 5000);

        const storage = {};
        storage['lastMsgTime'] = (new Date()).getTime();

        RPC.addRoute('whoAreYou', (data) => {
            return w.navigator.userAgent;
        });

        RPC.addRoute('time', (data) => {
            RPC.call('time', (new Date()).getTime());
        });

        RPC.addRoute('incoming', addMessage);
        RPC.addRoute('update_users', updateUsers);
        RPC.connect();

        function updateUsers(e) {
            //
        }

        function addMessage(e) {
            setTimeout(() => {
                d.querySelector('.messages-list').scrollTop += 500;
            }, 10);
            if (vm.messages.length > 100) {
                vm.messages.shift()
            }
            vm.messages.push(e);
        }

        Vue.component('modal', {
            template: '#config-modal'
        });

        const vm = new Vue({
            el: '#messages-list',
            data: {
                messages: [],
                users: [],
                value: '',
                active: false,
                showLoader: true
            },
            methods: {
                sendMessage: function (e) {
                    let _ = this;

                    if (_.active && !_.value.length) {
                        return;
                    }

                    RPC.call('message', _.value).then(() => {
                        _.value = ''
                    });
                },
                closeThisMessage: function (e) {
                    e.target.closest('.message').remove();
                },
                replay: function (item) {
                    console.log(item);
                }
            }
        });

        const vm2 = new Vue({
            el: '#login-block',
            template: '#login-block-tpl',
            data: {
                active: false,
                login: '',
                password: '',
                email: '',
                errors: [
                    // {type: 'alert-warning', text: 'error1'}, {type: 'alert-info', text: 'error2'},
                ],
                showEmail: true,
                showSignUpButton: true,
                showSignInPanel: false,
                showModal: false,
                parentClick: null,
            },
            // beforeMount: (e) => {
            //     let _ = this;
            //     post('/user/check', {})
            //         .then((e) => { return e.json(); })
            //         .then((e) => {
            //             _.active = e.result;
            //             });
            // },
            methods: {
                signIn: function (e) {
                    let _ = this;
                    post('/user/signin', {
                            login: _.login
                            , password: _.password
                        })
                        .then((e) => {
                            return e.json();
                        })
                        .then((e) => {
                            _.active = vm.active = e.result;
                            _.errors = e.errors;
                            _.showSignInPanel = !e.result;
                        });
                },
                signUp: function (e) {
                    let _ = this;
                    post('/user/signup', {
                            login: _.login
                            , password: _.password
                            , email: _.email
                        })
                        .then((e) => {
                            return e.json();
                        })
                        .then((e) => {
                            _.active = vm.active = e.result;
                            _.errors = e.errors;
                            _.showSignInPanel = !e.result;
                        });
                },
                logOut: function (e) {
                    let _ = this;
                    post('/user/logout').then(() => {
                        _.active = vm.active = false;
                    })
                },
                show: function (e) {
                    if(this.showSignInPanel && this.parentClick === e) {
                        this.showSignInPanel = false;
                    }
                    else {
                        this.parentClick = e;
                        this.showSignInPanel = true;
                        this.showEmail = this.showSignUpButton = (e === 'signUp');
                    }
                }
            }
        });

        post('/user/messages', {})
            .then((e) => {
                return e.json();
            })
            .then((e) => {
                if (e.items.length) {
                    vm.messages = e.items;
                    setTimeout(() => {
                        d.querySelector('.messages-list').scrollTop = 5000;
                    }, 10);
                }
            });

        RPC.addEventListener('onconnect', function (e) {
            post('/user/check')
                .then((e) => {
                    return e.json();
                })
                .then((e) => {
                    vm.showLoader = false;
                    vm.active = vm2.active = e.result;
                    vm.users = e.users;
                });
        });
        RPC.addEventListener('onerror', function (e) {
            vm.active = false;
            vm.showLoader = true;
        });
        RPC.addEventListener('onclose', function (e) {
            vm.active = false;
            vm.showLoader = true;
        });
    });
})(document, window);
