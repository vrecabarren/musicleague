class VoteControl extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            uri: props.uri,
            points: 0
        };
    }

    render() {
        var stateClass = (this.state.points < 0) ? "downVoted" : (this.state.points > 0) ? "upVoted" : "";
        return (
            <div className={"col-sm-5 col-md-4 col-height voteControl" + " " + stateClass}>
                <div className="voteControlInner">
                    <span className="downButton" onClick={this.downVote.bind(this)}></span>
                    <span className="pointCount">{Math.abs(this.state.points)}</span>
                    <span className="upButton" onClick={this.upVote.bind(this)}></span>
                    <div className="statusIconWrapper">
                        <span className="statusIcon"></span>
                    </div>
                </div>
            </div>
        );
    }

    downVote() {
        var newPointValue = this.state.points - 1;
        if (this.props.minPoints == null || newPointValue >= this.props.minPoints) {
            var downVoteAllowed = this.props.onDownVote(this.state.uri, newPointValue);
            if (downVoteAllowed)
                this.setState({points: this.state.points - 1});
        } else {
            console.log("Down vote count " + Math.abs(newPointValue) + " exceeds per-song allowance. Rejecting.")
        }
    }

    upVote() {
        var newPointValue = this.state.points + 1;
        if (this.props.maxPoints == null || newPointValue <= this.props.maxPoints) {
            var upVoteAllowed = this.props.onUpVote(this.state.uri, newPointValue);
            if (upVoteAllowed)
                this.setState({points: this.state.points + 1});
        } else {
            console.log("Up vote count " + newPointValue + " exceeds per-song allowance. Rejecting.")
        }
    }
}

class VoteControlMobile extends VoteControl {
    render() {
        var stateClass = (this.state.points < 0) ? "downVoted" : (this.state.points > 0) ? "upVoted" : "";
        return (
            <div className={"col-xs-6 col-height voteControl" + " " + stateClass}>
                <div className="voteControlInner">
                    <span className="downButton" onClick={this.downVote.bind(this)}></span>
                    <span className="pointCount">{Math.abs(this.state.points)}</span>
                    <span className="upButton" onClick={this.upVote.bind(this)}></span>
                </div>
                <div className="statusIconWrapper">
                    <span className="statusIcon"></span>
                </div>
            </div>
        );
    }
}

class SongInfo extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            uri: props.uri,
            track: {name: '',
                    artists: [{name: ''}],
                    album: {images: [{}, {url: ''}], name: ''}
            }
        }
    }

    componentDidMount() {
        // Get track object from Spotify API
        var trackId = this.state.uri.match(/spotify\:track\:([a-zA-Z0-9]{22})/)[1];
        axios.get('https://api.spotify.com/v1/tracks/' + trackId).then(res => {
            this.setState({track: res.data});
        });
    }

    render() {
        return (
            <div className="col-sm-7 col-md-8 songInfo">
                <img src={this.state.track.album.images[1].url} className="img img-rounded"/>
                <div className="textInfo">
                    <span className="trackName">{this.state.track.name}</span>
                    <span className="trackArtist">By {this.state.track.artists[0].name}</span>
                    <span className="trackAlbum">{ this.state.track.album.name }</span>
                </div>
            </div>
        );
    }
}

class SongInfoMobile extends SongInfo {
    render() {
        return (
            <div className="col-xs-6 col-height songInfo">
                <img src={this.state.track.album.images[1].url} className="img img-rounded"/>
                <div className="textInfo">
                    <span className="trackName">{this.state.track.name}</span>
                    <span className="trackArtist">By {this.state.track.artists[0].name}</span>
                    <span className="trackAlbum">{ this.state.track.album.name }</span>
                </div>
            </div>
        );
    }
}

class Song extends React.Component {
    render() {
        return (
            <div className="song row">
                <div className="hidden-xs">
                    <SongInfo uri={this.props.uri}/>
                    <VoteControl maxPoints={null} minPoints={null} uri={this.props.uri} onUpVote={this.props.onUpVote} onDownVote={this.props.onDownVote}/>
                </div>
            </div>
         );
    }
}

class SongMobile extends Song {
    render() {
        return (
            <div className="song row">
                <div className="visible-xs">
                    <div className="row-height">
                        <SongInfoMobile uri={this.props.uri}/>
                        <VoteControlMobile maxPoints={null} minPoints={null} uri={this.props.uri} onUpVote={this.props.onUpVote} onDownVote={this.props.onDownVote}/>
                    </div>
                </div>
            </div>
         );
    }
}

class SongListHeader extends React.Component {
    render() {
        return (
            <div className="songListHeader">
                <div className="container">
                    <div className="row">
                        <div className="hidden-xs col-sm-4 col-md-4 vcenter text-center">
                            <span>Choose A Song And Add Points To Begin!</span>
                        </div>
                        <div className="col-xs-6 col-ms-3 col-md-4 vcenter text-center">
                            <div className="progressWrapper">
                                <span className="progressIndicator">
                                    <span className="numSpent">{this.props.upVotes > 9 ? ""+this.props.upVotes: "0"+this.props.upVotes}</span> of <span className="maxVotes">{this.props.maxUpVotes > 9 ? ""+this.props.maxUpVotes: "0"+this.props.maxUpVotes}</span>
                                </span>
                                <span className="statusIcon upVote"></span>
                            </div>
                        </div>
                        <div className={this.props.enabled ? 'col-xs-6 col-sm-5 col-md-4 vcenter text-center' : 'col-xs-6 col-sm-5 col-md-4 vcenter text-center disabled'} id="submitVotesButtonWrapper">
                            <button type="submit" id="submitVotesButton" className={this.props.enabled ? 'btn btn-lg' : 'btn btn-lg disabled'} disabled={!this.props.enabled}>Submit<span className="hidden-xs"> Votes</span>!</button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

class SongListHeaderWithDownVotes extends React.Component {
    render() {
        return (
            <div className="songListHeader">
                <div className="container">
                    <div className="row">
                        <div className="col-xs-6 col-ms-3 col-md-4 vcenter text-center">
                            <div className="progressWrapper">
                                <span className="progressIndicator">
                                    <span className="numSpent">{this.props.upVotes > 9 ? ""+this.props.upVotes: "0"+this.props.upVotes}</span> of <span className="maxVotes">{this.props.maxUpVotes > 9 ? ""+this.props.maxUpVotes: "0"+this.props.maxUpVotes}</span>
                                </span>
                                <span className="statusIcon upVote"></span>
                            </div>
                        </div>
                        <div className="col-xs-6 col-ms-3 col-md-4 vcenter text-center">
                            <div className="progressWrapper">
                                <span className="progressIndicator">
                                    <span className="numSpent">{this.props.downVotes > 9 ? ""+this.props.downVotes: "0"+this.props.downVotes}</span> of <span className="maxVotes">{this.props.maxDownVotes > 9 ? ""+this.props.maxDownVotes: "0"+this.props.maxDownVotes}</span>
                                </span>
                                <span className="statusIcon downVote"></span>
                            </div>
                        </div>
                        <div className={this.props.enabled ? 'col-xs-6 col-sm-5 col-md-4 vcenter text-center' : 'col-xs-6 col-sm-5 col-md-4 vcenter text-center disabled'} id="submitVotesButtonWrapper">
                            <button type="submit" id="submitVotesButton" className={this.props.enabled ? 'btn btn-lg' : 'btn btn-lg disabled'} disabled={!this.props.enabled}>Submit<span className="hidden-xs"> Votes</span>!</button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

class SongList extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            upVotes: 0,
            downVotes: 0,
            votes: {}
        };
    }

    render() {
        var listHeader = null;
        var headerEnabled = (this.state.upVotes == this.props.maxUpVotes) && (this.props.maxDownVotes == null || (this.state.downVotes == this.props.maxDownVotes));

        if (this.props.maxDownVotes == null) {
            listHeader = <SongListHeader upVotes={this.state.upVotes} maxUpVotes={this.props.maxUpVotes} enabled={headerEnabled}/>;
        } else {
            listHeader = <SongListHeaderWithDownVotes upVotes={this.state.upVotes} maxUpVotes={this.props.maxUpVotes} downVotes={this.state.downVotes} maxDownVotes={this.props.maxDownVotes} enabled={headerEnabled}/>;
        }

        return (
            <div>
                <form onSubmit={this.handleFormSubmission.bind(this)}>
                    {listHeader}
                    <div className="songList">
                        <div className="container">
                            {
                                // TODO: Pass min/max points allowed per song, null if not set
                                this.props.uris.map(function(uri) {
                                    return (
                                        <div>
                                            <Song uri={uri} onUpVote={this.onUpVote.bind(this)} onDownVote={this.onDownVote.bind(this)}/>
                                            <SongMobile uri={uri} onUpVote={this.onUpVote.bind(this)} onDownVote={this.onDownVote.bind(this)}/>
                                        </div>
                                    );
                                }.bind(this))
                            }
                        </div>
                    </div>
                </form>
            </div>
        );
    }

    handleFormSubmission() {
        console.log("Form submitted: " + JSON.stringify(this.state.votes));
        return false;
    }

    onUpVote(uri, newPointValue) {
        /* When a song in the SongList is upvoted, we need to determine
        whether the user is removing a downvote or adding an upvote. If
        the user is adding an upvote, we need to reject the upvote when
        it exceeds the allowance.
        */
        if (newPointValue <= 0) {
            console.log("Song vote " + newPointValue + " is still negative. Will allow.");
            var newVotesState = this.state.votes;
            newVotesState[uri] = newPointValue;
            this.setState({downVotes: this.state.downVotes - 1, votes: newVotesState});
        }

        else {
            var newUpVotesValue = this.state.upVotes + 1;

            if (newUpVotesValue <= this.props.maxUpVotes) {
                console.log("Up vote count " + newUpVotesValue + " within allowance. Will allow.");
                var newVotesState = this.state.votes;
                newVotesState[uri] = newPointValue;
                this.setState({upVotes: this.state.upVotes + 1, votes: newVotesState});
            }

            else {
                console.log("Up vote count " + newUpVotesValue + " exceeds total allowance. Rejecting.");
                return false;
            }
        }

        return true;
    }

    onDownVote(uri, newPointValue) {
        /* When a song in the SongList is downvoted, we need to determine
        whether the user is removing an upvote or adding a downvote. If
        the user is adding a downvote, we need to reject the downvote When
        it exceeds the allowance.
        */
        if (newPointValue >= 0) {
            console.log("Song vote " + newPointValue + " is still positive. Will allow.");
            var newVotesState = this.state.votes;
            newVotesState[uri] = newPointValue;
            this.setState({upVotes: this.state.upVotes - 1, votes: newVotesState});
        }

        else {
            var newDownVotesValue = this.state.downVotes + 1;

            if (newDownVotesValue <= this.props.maxDownVotes) {
                console.log("Down vote count " + newDownVotesValue + " within allowance. Will allow.");
                var newVotesState = this.state.votes;
                newVotesState[uri] = newPointValue;
                this.setState({downVotes: this.state.downVotes + 1, votes: newVotesState});
            }

            else {
                console.log("Down vote count " + newDownVotesValue + " exceeds total allowance. Rejecting.");
                return false;
            }
        }

        return true;
    }
}

/*
NOTE: Currently rendered on template in order to inject data prior to page load
ReactDOM.render(
    <SongList
        uris={["spotify:track:429EttO8gs0bDo2SQfUNSm", "spotify:track:5Ykzu4eg5UEVJP3LCoxgpF", "spotify:track:6DXFVsLcEvOTSrkG9G1Cb1", "spotify:track:6GyFP1nfCDB8lbD2bG0Hq9", "spotify:track:0x4rW5jv6fkKweBgjE5O8F"]}
        maxDownVotes={0} maxUpVotes={10}/>,
    document.getElementById('mountVote')
);
*/
