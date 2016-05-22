/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 */

import React, { Component } from 'react';
import {
  AppRegistry,
  StyleSheet,
  Text,
  TextInput,
  ScrollView,
  View,
} from 'react-native';

class MessageRow extends Component {

  render () {
    return (
      <Text style={styles.message, styles.self}>
        The message is {this.props.message}
      </Text>
    );
  }
}

class MessageListView extends Component {

  render () {
    return (
      <ScrollView>
        {this.props.messages.map((message, i) => <MessageRow message={message} key={i}/>)}
      </ScrollView>
   );
 }
}

class MainView extends Component {

  constructor (props) {
    super(props);
    this.state={messages: []};
  }

  onSubmiting(text) {
    this.state.messages.push(text);
    this.setState({messages: this.state.messages});
  }

  render() {
    return (
      <View style={styles.container}>
        <MessageListView
          messages={this.state.messages}
        />
        <TextInput
				  onSubmitEditing={(text) => { this.onSubmiting(this.state.text)}}
					style={{height: 40, borderColor: 'gray', borderWidth: 1}}
					onChangeText={(text) => this.setState({text})}
				/>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    backgroundColor: '#F5FCFF',
  },
  message: {
    fontSize: 50,
    color: '#333333',
    margin: 10,
  },
  self: {
    textAlign: 'right',
  },
  someoneElse: {
    textAlign: 'left',

	}
});

AppRegistry.registerComponent('app', () => MainView);
