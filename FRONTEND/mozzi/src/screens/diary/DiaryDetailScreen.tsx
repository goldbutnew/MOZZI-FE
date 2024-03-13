import { View, Text, TouchableOpacity, Image } from 'react-native'
import React from 'react'
import Icon from 'react-native-vector-icons/MaterialIcons'
import styled from 'styled-components/native'

import { useNavigation } from '@react-navigation/native'

const Container = styled.View`
  flex: 1;
  background-color: #FFFEF2;
`

const Title = styled.Text`
  font-size: 20px;
  margin: 30px 0px 30px 20px;
`

const Dot = styled.Text`
  color: #E4E196;
`

const Body = styled.View`
  align-self: center;
  align-items: center;
  justify-content: center;
  width: 350px;
  height: 400px;
  border-radius: 20px;
  background-color: #F9F7BB;
`

const Btn = styled.TouchableOpacity`
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 28px;
  position: absolute;
  top: 28px;
  right: 30px;
`

const FoodImage = styled.Image`
  width: 300px;
  height: 300px;
  border-radius: 5px;
`

const FoodTitle = styled.Text`
  font-size: 15px;
  font-weight: bold;
  margin-bottom: 10px;
`

function DiaryDetailScreen ({ route }) {
  const { date } = route.params
  const navigation = useNavigation()

  const goBack = () => {
   navigation.goBack()
  }

  const moveShared = () => {
    navigation.navigate("")
  }

  return (
    <>
      <Container>
        <TouchableOpacity onPress={goBack}>
          <Icon name="keyboard-arrow-left" size={35} color="black" />
        </TouchableOpacity>
        <View>
          <Title> <Dot>●   </Dot> {date.year}년 {date.month}월 {date.day}일 요리 일기</Title>
        </View>

        <Body>
          <View>
            <FoodTitle>비비큐 황금올리브</FoodTitle>
            <FoodImage
              source={require('../../assets/recommend/chicken.jpg')}
            />
          </View>
          <Btn onPress={moveShared}>
            <Icon name="ios-share" size={24} color="black" />
          </Btn>
        </Body>
      </Container>
    </>
  )
}

export default DiaryDetailScreen