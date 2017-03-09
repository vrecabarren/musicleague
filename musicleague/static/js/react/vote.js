"use strict";

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var VoteControl = function (_React$Component) {
    _inherits(VoteControl, _React$Component);

    function VoteControl(props) {
        _classCallCheck(this, VoteControl);

        var _this = _possibleConstructorReturn(this, (VoteControl.__proto__ || Object.getPrototypeOf(VoteControl)).call(this, props));

        _this.state = {
            points: 0
        };
        return _this;
    }

    _createClass(VoteControl, [{
        key: "render",
        value: function render() {
            var stateClass = this.state.points < 0 ? "downVoted" : this.state.points > 0 ? "upVoted" : "";
            return React.createElement(
                "div",
                { className: "voteControl" + " " + stateClass },
                React.createElement(
                    "div",
                    { className: "voteControlInner" },
                    React.createElement("span", { className: "downButton", onClick: this.downVote.bind(this) }),
                    React.createElement(
                        "span",
                        { className: "pointCount" },
                        this.state.points
                    ),
                    React.createElement("span", { className: "upButton", onClick: this.upVote.bind(this) })
                )
            );
        }
    }, {
        key: "downVote",
        value: function downVote() {
            var newPointValue = this.state.points - 1;
            if (newPointValue >= this.props.minPoints) {
                var downVoteAllowed = this.props.onDownVote(newPointValue);
                if (downVoteAllowed) this.setState({ points: this.state.points - 1 });
            } else {
                console.log("Down vote count " + Math.abs(newPointValue) + " exceeds per-song allowance. Rejecting.");
            }
        }
    }, {
        key: "upVote",
        value: function upVote() {
            var newPointValue = this.state.points + 1;
            if (newPointValue <= this.props.maxPoints) {
                var upVoteAllowed = this.props.onUpVote(newPointValue);
                if (upVoteAllowed) this.setState({ points: this.state.points + 1 });
            } else {
                console.log("Up vote count " + newPointValue + " exceeds per-song allowance. Rejecting.");
            }
        }
    }]);

    return VoteControl;
}(React.Component);

var SongInfo = function (_React$Component2) {
    _inherits(SongInfo, _React$Component2);

    function SongInfo(props) {
        _classCallCheck(this, SongInfo);

        var _this2 = _possibleConstructorReturn(this, (SongInfo.__proto__ || Object.getPrototypeOf(SongInfo)).call(this, props));

        _this2.state = {
            uri: props.uri,
            track: { name: '',
                artists: [{ name: '' }],
                album: { images: [{}, { url: '' }] }
            }
        };
        return _this2;
    }

    _createClass(SongInfo, [{
        key: "componentDidMount",
        value: function componentDidMount() {
            var _this3 = this;

            // Get track object from Spotify API
            var trackId = this.state.uri.match(/spotify\:track\:([a-zA-Z0-9]{22})/)[1];
            axios.get('https://api.spotify.com/v1/tracks/' + trackId).then(function (res) {
                _this3.setState({ track: res.data });
            });
        }
    }, {
        key: "render",
        value: function render() {
            return React.createElement(
                "div",
                { className: "songInfo" },
                React.createElement("img", { src: this.state.track.album.images[1].url, className: "rounded" }),
                React.createElement(
                    "div",
                    { className: "textInfo" },
                    React.createElement(
                        "span",
                        { className: "trackName" },
                        this.state.track.name
                    ),
                    React.createElement(
                        "span",
                        { className: "trackArtist" },
                        "By ",
                        this.state.track.artists[0].name
                    )
                )
            );
        }
    }]);

    return SongInfo;
}(React.Component);

var Song = function (_React$Component3) {
    _inherits(Song, _React$Component3);

    function Song() {
        _classCallCheck(this, Song);

        return _possibleConstructorReturn(this, (Song.__proto__ || Object.getPrototypeOf(Song)).apply(this, arguments));
    }

    _createClass(Song, [{
        key: "render",
        value: function render() {
            return React.createElement(
                "div",
                { className: "song row" },
                React.createElement(
                    "div",
                    { className: "col-md-8" },
                    React.createElement(SongInfo, { uri: this.props.uri })
                ),
                React.createElement(
                    "div",
                    { className: "col-md-4" },
                    React.createElement(VoteControl, { maxPoints: 10, minPoints: -5, onUpVote: this.props.onUpVote, onDownVote: this.props.onDownVote })
                )
            );
        }
    }]);

    return Song;
}(React.Component);

var SongList = function (_React$Component4) {
    _inherits(SongList, _React$Component4);

    function SongList(props) {
        _classCallCheck(this, SongList);

        var _this5 = _possibleConstructorReturn(this, (SongList.__proto__ || Object.getPrototypeOf(SongList)).call(this, props));

        _this5.state = {
            upVotes: 0,
            maxUpVotes: props.maxUpVotes,
            downVotes: 0,
            maxDownVotes: props.maxDownVotes
        };
        return _this5;
    }

    _createClass(SongList, [{
        key: "componentDidMount",
        value: function componentDidMount() {
            // TODO: Load required info such as up/downvote allowances and URIs
        }
    }, {
        key: "render",
        value: function render() {
            return React.createElement(
                "div",
                null,
                React.createElement(
                    "div",
                    { className: "songListHeader" },
                    React.createElement(
                        "div",
                        { className: "container" },
                        React.createElement(
                            "div",
                            { className: "row" },
                            React.createElement(
                                "div",
                                { className: "col-md-4 vcenter" },
                                React.createElement(
                                    "span",
                                    { id: "pasteDirective" },
                                    "Choose A Song And Add Points To Begin!"
                                )
                            ),
                            React.createElement(
                                "div",
                                { className: "col-md-4 vcenter" },
                                React.createElement(
                                    "span",
                                    { className: "progressIndicator" },
                                    React.createElement(
                                        "span",
                                        { className: "numSpent" },
                                        this.state.upVotes
                                    ),
                                    " of ",
                                    React.createElement(
                                        "span",
                                        { className: "maxVotes" },
                                        this.state.maxUpVotes
                                    )
                                ),
                                React.createElement("br", null),
                                React.createElement(
                                    "span",
                                    null,
                                    "Points Spent"
                                )
                            ),
                            React.createElement("div", { className: "col-md-4 vcenter" })
                        )
                    )
                ),
                React.createElement(
                    "div",
                    { className: "container" },
                    React.createElement(
                        "div",
                        { className: "songList" },
                        this.props.uris.map(function (uri) {
                            return React.createElement(Song, { uri: uri, onUpVote: this.onUpVote.bind(this), onDownVote: this.onDownVote.bind(this) });
                        }.bind(this))
                    )
                )
            );
        }
    }, {
        key: "onUpVote",
        value: function onUpVote(newPointValue) {
            /* When a song in the SongList is upvoted, we need to determine
            whether the user is removing a downvote or adding an upvote. If
            the user is adding an upvote, we need to reject the upvote when
            it exceeds the allowance.
            */
            if (newPointValue <= 0) {
                console.log("Song vote " + newPointValue + " is still negative. Will allow.");
                this.setState({ downVotes: this.state.downVotes - 1 });
            } else {
                var newUpVotesValue = this.state.upVotes + 1;

                if (newUpVotesValue <= this.state.maxUpVotes) {
                    console.log("Up vote count " + newUpVotesValue + " within allowance. Will allow.");
                    this.setState({ upVotes: this.state.upVotes + 1 });
                } else {
                    console.log("Up vote count " + newUpVotesValue + " exceeds total allowance. Rejecting.");
                    return false;
                }
            }

            return true;
        }
    }, {
        key: "onDownVote",
        value: function onDownVote(newPointValue) {
            /* When a song in the SongList is downvoted, we need to determine
            whether the user is removing an upvote or adding a downvote. If
            the user is adding a downvote, we need to reject the downvote When
            it exceeds the allowance.
            */
            if (newPointValue >= 0) {
                console.log("Song vote " + newPointValue + " is still positive. Will allow.");
                this.setState({ upVotes: this.state.upVotes - 1 });
            } else {
                var newDownVotesValue = this.state.downVotes + 1;

                if (newDownVotesValue <= this.state.maxDownVotes) {
                    console.log("Down vote count " + newDownVotesValue + " within allowance. Will allow.");
                    this.setState({ downVotes: this.state.downVotes + 1 });
                } else {
                    console.log("Down vote count " + newDownVotesValue + " exceeds total allowance. Rejecting.");
                    return false;
                }
            }

            return true;
        }
    }]);

    return SongList;
}(React.Component);

ReactDOM.render(React.createElement(SongList, {
    uris: ["spotify:track:429EttO8gs0bDo2SQfUNSm", "spotify:track:5Ykzu4eg5UEVJP3LCoxgpF", "spotify:track:6DXFVsLcEvOTSrkG9G1Cb1", "spotify:track:6GyFP1nfCDB8lbD2bG0Hq9", "spotify:track:0x4rW5jv6fkKweBgjE5O8F"],
    maxDownVotes: 5, maxUpVotes: 10 }), document.getElementById('mountVote'));