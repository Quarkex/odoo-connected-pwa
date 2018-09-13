'use strict';

const e = React.createElement;

class LikeButton extends React.Component {
    constructor(props) {
        super(props);
        this.state = { liked: false };
    }

    render() {
        if (this.state.liked) {
            return 'You liked this. React powered.';
        }

        return e(
            'span',
            { onClick: () => this.setState({ liked: true }) },
            'React like button'
        );
    }
}

const domContainer = document.querySelector('#react_component');
ReactDOM.render(e(LikeButton), domContainer);
