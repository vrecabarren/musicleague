class MiniLeaderboard extends React.Component {
    render() {
        var league = this.props.league;
        const wrapperStyle = {
            backgroundColor: "rgba(1, 36, 154, 0.85)",
            borderRadius: "8px",
            marginTop: "25px",
            padding: "20px 0px"
        }
        return (
            <div className="rankingsWrapper" style={wrapperStyle}>
                <div className="row">
                    <div className="col-md-4"><MiniLeaderboardEntry entry={league.scoreboard.rankings[1][0]} rank="first"/></div>
                    <div className="col-md-4"><MiniLeaderboardEntry entry={league.scoreboard.rankings[2][0]} rank="second"/></div>
                </div>
            </div>
        );
    }
}

class MiniLeaderboardEntry extends React.Component {
    render() {
        var entry = this.props.entry;
        var rank = this.props.rank;
        const pointsStyle = {
            color: "#F8C62C",
            fontFamily: '"Cubano", sans-serif',
            fontSize: "40px",
            marginRight: "10px",
            verticalAlign: "middle"
        };
        const nameStyle = {verticalAlign: "middle"};
        return (
            <div>
                <span className={"rank " + rank}></span>
                <span className="points" style={pointsStyle}>{entry.points}</span>
                <span className="name" style={nameStyle}>{entry.user.name}</span>
            </div>
        );
    }
}

var league = {
    name: "ML: Decades",
    scoreboard: {
        rankings: {
            1: [{user: {name: "Nathan Coleman"},
                 points: 22}],
            2: [{user: {name: "Katherine Carnes Coleman"},
                 points: 19}],
        }
    }
}

ReactDOM.render(<MiniLeaderboard league={league}/>, document.getElementById('mountMiniLeaderboard'));
