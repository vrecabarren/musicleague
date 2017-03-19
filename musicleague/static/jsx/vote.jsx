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
            <div className="col-sm-4 col-md-4 col-height col-middle" style={{padding: '0'}}>
                <div className="progressWrapper" ref={(div) => { this.progressWrapper = div; }}>
                    <div className={"voteControl" + " " + stateClass}>
                        <div className="voteControlInner">
                            <span className={this.state.points == (this.props.maxDownVotes * -1) ? "downButton disabled" : "downButton" } onClick={this.downVote.bind(this)}></span>
                            <span className="pointCount">{Math.abs(this.state.points) > 9 ? ""+Math.abs(this.state.points) : "0"+Math.abs(this.state.points)}</span>
                            <span className={this.state.points == this.props.maxUpVotes ? "upButton disabled" : "upButton" } onClick={this.upVote.bind(this)}></span>
                            <div className="statusIconWrapper">
                                <span className="statusIcon"></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    downVote() {
        var newPointValue = this.state.points - 1;
        if (this.props.maxDownVotes == null || newPointValue >= 0 || (Math.abs(newPointValue) <= this.props.maxDownVotes)) {
            var downVoteAllowed = this.props.onDownVote(this.state.uri, newPointValue);
            if (downVoteAllowed) {
                this.setState({points: newPointValue});
                this.adjustProgress(newPointValue);
            }
        } else {
            console.log("Down vote count " + Math.abs(newPointValue) + " exceeds per-song allowance of " + this.props.maxDownVotes + ". Rejecting.")
        }
    }

    upVote() {
        var newPointValue = this.state.points + 1;
        if (this.props.maxUpVotes == null || newPointValue <= 0 || newPointValue <= this.props.maxUpVotes) {
            var upVoteAllowed = this.props.onUpVote(this.state.uri, newPointValue);
            if (upVoteAllowed) {
                this.setState({points: newPointValue});
                this.adjustProgress(newPointValue);
            }
        } else {
            console.log("Up vote count " + newPointValue + " exceeds per-song allowance of " + this.props.maxUpVotes + ". Rejecting.")
        }
    }

    adjustProgress(newPointValue) {
        if (this.progressWrapper == null)
            return;

        var height = this.progressWrapper.offsetHeight;
        var edgeHeight = height - 5;
        var width = this.progressWrapper.offsetWidth;
        var edgeWidth = width - 5;

        if (newPointValue >= 0) {
            var progress = newPointValue / this.props.maxUpVotes;
            var progressColor = "#5FCC34";
        } else {
            var progress = Math.abs(newPointValue) / this.props.maxDownVotes;
            var progressColor = "#D21E35";
        }
        var totalLength = (width * 2) + (height * 2);
        var borderLen = progress * totalLength;

        // If progress can be expressed on top border alone
        if (borderLen <= width) {
            var backgroundPos = 'background-position: ' + ((width * -1) + borderLen) + 'px 0px, ' + edgeWidth + 'px ' + (height * -1) + 'px, ' + width + 'px ' + edgeHeight + 'px, 0px ' + height + 'px;';
            this.progressWrapper.setAttribute('style', backgroundPos);
        }
        // If progress can be expressed on top and right borders alone
        else if (borderLen <= (width + height)) {
            var backgroundPos = 'background-position: 0px 0px, ' + edgeWidth + 'px ' + ((height * -1) + (borderLen - width)) + 'px, ' + width + 'px ' + edgeHeight + 'px, 0px ' + height + 'px';
            this.progressWrapper.setAttribute('style', backgroundPos);
        }
        // If progress can be expressed on top, right, and bottom borders alone
        else if (borderLen <= (width * 2 + height)) {
            var backgroundPos = 'background-position: 0px 0px, ' + edgeWidth + 'px 0px, ' + (width - (borderLen - width - height)) + 'px ' + edgeHeight + 'px, 0px ' + height + 'px';
            this.progressWrapper.setAttribute('style', backgroundPos);
        }
        // If progress needs all four borders to be expressed
        else {
            var backgroundPos = 'background-position: 0px 0px, ' + edgeWidth + 'px 0px, 0px ' + edgeHeight + 'px, 0px ' + (height - (borderLen - (width * 2) - height)) + 'px';
            this.progressWrapper.setAttribute('style', backgroundPos);
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
            <div className="col-sm-8 col-md-8 col-height col-middle songInfo">
                <img src={this.state.track.album.images[1].url}/>
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
                <img src={this.state.track.album.images[1].url}/>
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
            <div className="hidden-xs">
                <div className="song full row">
                    <div className="row-height">
                        <SongInfo uri={this.props.uri}/>
                        <VoteControl maxUpVotes={this.props.maxUpVotes} maxDownVotes={this.props.maxDownVotes} uri={this.props.uri} onUpVote={this.props.onUpVote} onDownVote={this.props.onDownVote}/>
                    </div>
                </div>
            </div>
         );
    }
}

class SongMobile extends Song {
    render() {
        return (
            <div className="visible-xs">
                <div className="song mobile row">
                    <div className="row-height">
                        <SongInfoMobile uri={this.props.uri}/>
                        <VoteControlMobile maxUpVotes={this.props.maxUpVotes} maxDownVotes={this.props.maxDownVotes} uri={this.props.uri} onUpVote={this.props.onUpVote} onDownVote={this.props.onDownVote}/>
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
                        <div className="hidden-xs">
                            <div className="row-height">
                                <div className="hidden-xs col-sm-4 col-md-4 vcenter text-center">
                                    <span>Choose A Song And Add Points To Begin!</span>
                                </div>
                                <div className="col-xs-6 col-sm-4 col-md-4 vcenter text-center" style={{borderLeft: "3px solid #fff"}}>
                                    <div className="progressWrapper">
                                        <span className="progressIndicator">
                                            <span className="numSpent">{this.props.upVotes > 9 ? ""+this.props.upVotes : "0"+this.props.upVotes}</span> of <span className="maxVotes">{this.props.maxUpVotes > 9 ? ""+this.props.maxUpVotes : "0"+this.props.maxUpVotes}</span>
                                        </span>
                                        <div className="statusIconWrapper">
                                            <span className="statusIcon upVote"></span>
                                        </div>
                                    </div>
                                </div>
                                <div className={this.props.enabled ? 'col-xs-6 col-sm-4 col-md-4 vcenter text-center' : 'col-xs-6 col-sm-4 col-md-4 vcenter text-center disabled'} id="submitVotesButtonWrapper">
                                    <button type="submit" id="submitVotesButton" className={this.props.enabled ? 'btn btn-lg' : 'btn btn-lg disabled'} disabled={!this.props.enabled}>Submit<span className="hidden-xs"> Votes</span>!</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

class SongListHeaderMobile extends SongListHeader {
    render() {
        return (
            <div className="songListHeader">
                <div className="container">
                    <div className="row">
                        <div className="visible-xs">
                            <div className="row-height">
                                <div className="col-xs-6 vcenter text-center">
                                    <div className="progressWrapper">
                                        <span className="progressIndicator">
                                            <span className="numSpent">{this.props.upVotes > 9 ? ""+this.props.upVotes: "0"+this.props.upVotes}</span> of <span className="maxVotes">{this.props.maxUpVotes > 9 ? ""+this.props.maxUpVotes : "0"+this.props.maxUpVotes}</span>
                                        </span>
                                        <div className="statusIconWrapper">
                                            <span className="statusIcon upVote"></span>
                                        </div>
                                    </div>
                                </div>
                                <div className={this.props.enabled ? 'col-xs-6 vcenter text-center' : 'col-xs-6 vcenter text-center disabled'} id="submitVotesButtonWrapper">
                                    <button type="submit" id="submitVotesButton" className={this.props.enabled ? 'btn btn-lg' : 'btn btn-lg disabled'} disabled={!this.props.enabled}>Submit<span className="hidden-xs"> Votes</span>!</button>
                                </div>
                            </div>
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
                    <div className="hidden-xs">
                        <div className="row">
                            <div className="row-height">
                                <div className="col-sm-4 col-md-4 vcenter text-center">
                                    <div className="progressWrapper">
                                        <span className="progressIndicator">
                                            <span className="numSpent">{this.props.upVotes > 9 ? ""+this.props.upVotes : "0"+this.props.upVotes}</span> of <span className="maxVotes">{this.props.maxUpVotes > 9 ? ""+this.props.maxUpVotes : "0"+this.props.maxUpVotes}</span>
                                        </span>
                                        <div className="statusIconWrapper">
                                            <span className="statusIcon upVote"></span>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-sm-4 col-md-4 vcenter text-center" style={{borderLeft: "3px solid #fff"}}>
                                    <div className="progressWrapper">
                                        <span className="progressIndicator">
                                            <span className="numSpent">{this.props.downVotes > 9 ? ""+this.props.downVotes : "0"+this.props.downVotes}</span> of <span className="maxVotes">{this.props.maxDownVotes > 9 ? ""+this.props.maxDownVotes : "0"+this.props.maxDownVotes}</span>
                                        </span>
                                        <div className="statusIconWrapper">
                                            <span className="statusIcon downVote"></span>
                                        </div>
                                    </div>
                                </div>
                                <div className={this.props.enabled ? 'col-sm-4 col-md-4 vcenter text-center' : 'col-sm-4 col-md-4 vcenter text-center disabled'} id="submitVotesButtonWrapper">
                                    <button type="submit" id="submitVotesButton" className={this.props.enabled ? 'btn btn-lg' : 'btn btn-lg disabled'} disabled={!this.props.enabled}>Submit<span className="hidden-xs"> Votes</span>!</button>
                                </div>
                            </div>
                            </div>
                    </div>
                </div>
            </div>
        );
    }
}

class SongListHeaderWithDownVotesMobile extends SongListHeaderWithDownVotes {
    render() {
        return (
            <div className="songListHeader">
                <div className="container">
                    <div className="visible-xs">
                        <div className="row">
                            <div className="row-height">
                                <div className="col-xs-6 col-height vcenter text-center">
                                    <div className="progressWrapper">
                                        <span className="progressIndicator">
                                            <span className="numSpent">{this.props.upVotes > 9 ? ""+this.props.upVotes: "0"+this.props.upVotes}</span> of <span className="maxVotes">{this.props.maxUpVotes > 9 ? ""+this.props.maxUpVotes: "0"+this.props.maxUpVotes}</span>
                                        </span>
                                        <div className="statusIconWrapper">
                                            <span className="statusIcon upVote"></span>
                                        </div>
                                    </div>
                                    <br/>
                                    <div className="progressWrapper">
                                        <span className="progressIndicator">
                                            <span className="numSpent">{this.props.downVotes > 9 ? ""+this.props.downVotes : "0"+this.props.downVotes}</span> of <span className="maxVotes">{this.props.maxDownVotes > 9 ? ""+this.props.maxDownVotes : "0"+this.props.maxDownVotes}</span>
                                        </span>
                                        <div className="statusIconWrapper">
                                            <span className="statusIcon downVote"></span>
                                        </div>
                                    </div>
                                </div>
                                <div className={this.props.enabled ? 'col-xs-6 col-height vcenter text-center' : 'col-xs-6 col-height vcenter text-center disabled'} id="submitVotesButtonWrapper">
                                    <button type="submit" id="submitVotesButton" className={this.props.enabled ? 'btn btn-lg' : 'btn btn-lg disabled'} disabled={!this.props.enabled}>Submit<span className="hidden-xs"> Votes</span>!</button>
                                </div>
                            </div>
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
        var mobileListHeader = null;
        var headerEnabled = (this.state.upVotes == this.props.maxUpVotes) && (!this.props.maxDownVotes || (this.state.downVotes == this.props.maxDownVotes));

        if (!this.props.maxDownVotes) {
            listHeader = <SongListHeader upVotes={this.state.upVotes} maxUpVotes={this.props.maxUpVotes} enabled={headerEnabled}/>;
            mobileListHeader = <SongListHeaderMobile upVotes={this.state.upVotes} maxUpVotes={this.props.maxUpVotes} enabled={headerEnabled}/>;
        } else {
            listHeader = <SongListHeaderWithDownVotes upVotes={this.state.upVotes} maxUpVotes={this.props.maxUpVotes} downVotes={this.state.downVotes} maxDownVotes={this.props.maxDownVotes} enabled={headerEnabled}/>;
            mobileListHeader = <SongListHeaderWithDownVotesMobile upVotes={this.state.upVotes} maxUpVotes={this.props.maxUpVotes} downVotes={this.state.downVotes} maxDownVotes={this.props.maxDownVotes} enabled={headerEnabled}/>;
        }

        return (
            <div>
                <form method="post" onSubmit={this.handleFormSubmission.bind(this)}>
                    {listHeader}
                    {mobileListHeader}
                    <div style={{padding: "15px 0"}}></div>
                    <div className="songList">
                        <div className="container">
                            {
                                // TODO: Pass min/max points allowed per song, null if not set
                                this.props.uris.map(function(uri) {
                                    return (
                                        <div>
                                            <Song uri={uri} maxUpVotes={this.props.maxUpVotesPerSong} maxDownVotes={this.props.maxDownVotesPerSong} onUpVote={this.onUpVote.bind(this)} onDownVote={this.onDownVote.bind(this)}/>
                                            <SongMobile uri={uri} maxUpVotes={this.props.maxUpVotesPerSong} maxDownVotes={this.props.maxDownVotesPerSong} onUpVote={this.onUpVote.bind(this)} onDownVote={this.onDownVote.bind(this)}/>
                                        </div>
                                    );
                                }.bind(this))
                            }
                        </div>
                    </div>
                    <input type="hidden" name="votes" id="votes"/>
                </form>
            </div>
        );
    }

    handleFormSubmission() {
        var votesJson = JSON.stringify(this.state.votes);
        document.getElementById('votes').value = votesJson;
        return true;
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
